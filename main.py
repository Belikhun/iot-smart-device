from wifi import start_access_point, stop_access_point, connect_wifi, start_wifi, stop_wifi, on_wifi_connected
from server import start_server, stop_server, is_portal_opened
from dns import do_start_dns_server
import uasyncio as asyncio
from logger import scope
from config import config, set_config
from client import ws_connect, ws_start_loop, ws_stop_loop, get_ws, ws_on_connected, ws_do_send, ws_on_data
from watchdog import start_watchdog
from device import init_features
from utils import hw_id, status_led, status_buzz, uuidv4
import machine

log = scope("main")
MAIN_INITIALIZED = False
CONFIGURE_STARTED = False

log("INFO", f"Hardware Id: {hw_id()}")

start_access_point()
start_wifi()

async def reset_device():
	log("WARN", ">>> RESETTING DEVICE...")
	log("WARN", ">>> RESETTING DEVICE...")
	log("WARN", ">>> RESETTING DEVICE...")
	await ws_stop_loop()
	stop_wifi()
	stop_server()
	stop_access_point()
	status_led().off()
	machine.reset()

def handle_ws_data(recv_data: dict):
	command = recv_data.get("command")

	if command == "reset":
		asyncio.create_task(reset_device())
		return True

	return False

ws_on_data(handle_ws_data)

def configure():
	global CONFIGURE_STARTED

	if not CONFIGURE_STARTED:
		start_server()
		do_start_dns_server()
		CONFIGURE_STARTED = True

async def main():
	status_buzz().do_beep(duration=0.2)

	on_wifi_connected(lambda: asyncio.create_task(initialized()))

	if not config("ssid"):
		log("INFO", "Device haven't been configured")
		status_led().start_animation("breathe", color=(0, 0, 255))
		configure()
		return

	connect_tries = 0

	while True:
		if is_portal_opened():
			log("INFO", "Detected a device opening configuration portal. Wifi reconnecting stopped.")

			stop_wifi()
			await asyncio.sleep(1)
			start_wifi()

			return

		connectSuccess = await connect_wifi()
		connect_tries += 1

		if not connectSuccess:
			if (connect_tries == 1):
				configure()
				log("WARN", "Wifi connection failed! Use configuration portal to re-configure network settings")

			if (connect_tries > 3):
				log("INFO", f"Wifi connection failed after {connect_tries} tries. Re-configuration required.")

				stop_wifi()
				await asyncio.sleep(1)
				start_wifi()

				return

			log("INFO", f"Retrying to connect in 2 seconds ({connect_tries}/3)")
			await asyncio.sleep(2)

			log("INFO", f"Restarting wifi interface...")
			stop_wifi()
			await asyncio.sleep(1)
			start_wifi()

			continue

		break

async def initialized():
	global MAIN_INITIALIZED

	if not MAIN_INITIALIZED:
		start_server()

	await asyncio.sleep_ms(500)
	await init_ws_server()
	MAIN_INITIALIZED = True

async def init_ws_server():
	if not config("server"):
		log("INFO", "Websocket server haven't been configured. Configuration is required in portal.")
		status_led().start_animation("breathe", color=(0, 255, 0))
		configure()
		return

	server_addr = "ws://{}/ws/device".format(config("server"))

	if (get_ws().is_open()):
		log("INFO", "Websocket is already opened, will perform a restart.")
		await get_ws().close()

	if not await ws_connect(server_addr):
		log("INFO", "Websocket server is not reachable. Re-configuration is required in portal.")
		status_led().start_animation("breathe", color=(0, 255, 0))
		configure()
		return

	stop_access_point()
	await ws_start_loop()

	log("OKAY", "Device initialized")

def handle_ws_connected():
	init_features()

	token = config("token")

	if not token:
		token = uuidv4()
		set_config("token", token, save=True)

	data = {
		"hardwareId": hw_id(),
		"name": config("name"),
		"token": token
	}

	ws_do_send("auth", data)

ws_on_connected(handle_ws_connected)

# Run the main loop
try:
	log("INFO", "Starting main program loop...")

	start_watchdog()
	asyncio.create_task(main())
	loop = asyncio.get_event_loop()
	loop.run_forever()
except KeyboardInterrupt:
	log("WARN", "Program loop stopped by user. Running clean up...")
	stop_wifi()
	stop_server()
	stop_access_point()
	status_led().off()
