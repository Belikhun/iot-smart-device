from wifi import start_access_point, stop_access_point, connect_wifi, start_wifi, stop_wifi, on_wifi_connected
from server import start_server, stop_server, is_portal_opened
from dns import do_start_dns_server
import uasyncio as asyncio
from logger import scope
from config import config
from utils import hw_id, status_led, status_buzz
from components import PushButton
from client import ws_connect, ws_start_loop, ws_do_send, get_ws
from watchdog import start_watchdog

log = scope("main")
MAIN_INITIALIZED = False
CONFIGURE_STARTED = False

log("INFO", f"Hardware Id: {hw_id()}")

start_access_point()
start_wifi()

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
	await asyncio.sleep_ms(500)
	
	if not MAIN_INITIALIZED:
		log("INFO", "Initializing board components...")
		button = PushButton(25)
		button.set_on_release(lambda: ws_do_send("led", {}))
		button.start_listen()

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
	ws_start_loop()

	log("OKAY", "Device initialized")

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
