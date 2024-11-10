from wifi import start_access_point, stop_access_point, connect_wifi, start_wifi
from server import start_server, stop_server
from dns import start_dns_server
import uasyncio as asyncio
from logger import scope
from config import config

log = scope("main")

start_access_point()
start_wifi()
start_server()

async def main():
	if not config("ssid"):
		log("INFO", "Device haven't been configured")
	else:
		connectSuccess = await connect_wifi()

		if not connectSuccess:
			log("WARN", "Wifi connection failed! Use configuration portal to re-configure network settings")

# Run the main loop
try:
	log("INFO", "Starting main program loop...")

	asyncio.create_task(start_dns_server())
	asyncio.create_task(main())
	loop = asyncio.get_event_loop()
	loop.run_forever()
except KeyboardInterrupt:
	log("WARN", "Program loop stopped by user. Running clean up...")
	stop_server()
	stop_access_point()
