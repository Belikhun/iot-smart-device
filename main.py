from wifi import start_access_point, stop_access_point, connect_wifi, start_wifi, stop_wifi
from server import start_server, stop_server
from dns import start_dns_server
import uasyncio as asyncio
from logger import scope
from config import config
from utils import hw_id, status_led, status_buzz
from components import PushButton
from client import ws_connect, ws_start_loop
from watchdog import start_watchdog

log = scope("main")

log("INFO", f"Hardware Id: {hw_id()}")

start_access_point()
start_wifi()

async def configure():
	start_server()
	asyncio.create_task(start_dns_server())

async def main():
	status_buzz().do_beep(duration=0.2)

	if not config("ssid"):
		log("INFO", "Device haven't been configured")
		status_led().start_animation("breathe", color=(0, 0, 255))
		await configure()
	else:
		connectSuccess = await connect_wifi()

		if not connectSuccess:
			await configure()
			log("WARN", "Wifi connection failed! Use configuration portal to re-configure network settings")
		else:
			await initialized()

async def initialized():
	log("INFO", "Initializing board components...")
	button = PushButton(25)
	button.set_on_press(lambda: log("INFO", "button 1 pressed"))
	button.start_listen()
	await init_ws_server()

async def init_ws_server():
	if not config("server"):
		log("INFO", "Websocket server haven't been configured. Configuration is required in portal.")
		return

	server_addr = "ws://{}/ws/device".format(config("server"))

	if not await ws_connect(server_addr):
		log("INFO", "Websocket server is not reachable. Re-configuration is required in portal.")
		configure()
		return

	stop_access_point()
	ws_start_loop()

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
