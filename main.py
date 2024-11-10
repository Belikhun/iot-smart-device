from wifi import start_access_point, stop_access_point, connect_wifi
from server import start_server, stop_server
from dns import start_dns_server
import uasyncio as asyncio
from logger import scope
from config import config

log = scope("main")

async def main():
	if not config("ssid"):
		log("INFO", "Device haven't been configured, starting configuration protocol...")
		start_access_point()
		start_server()
	else:
		connectSuccess = await connect_wifi()
		start_server()

		# if not connectSuccess:
		# 	log("WARN", "Wifi connection failed! Falling back to configuration protocol...")
		# 	start_access_point()
		# 	start_server()

# Run the main loop
try:
	log("INFO", "Starting main program loop...")

	asyncio.run(main())
	asyncio.run(start_dns_server())
	loop = asyncio.get_event_loop()
	loop.run_forever()
except KeyboardInterrupt:
	log("WARN", "Program loop stopped by user. Running clean up...")
	stop_server()
	stop_access_point()
