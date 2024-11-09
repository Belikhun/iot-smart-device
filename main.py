from wifi import start_access_point, stop_access_point, connect_wifi
from server import start_server, stop_server
from dns import start_dns_server
import uasyncio as asyncio
from logger import scope

log = scope("main")
start_access_point()
start_server()

async def main():
	await connect_wifi("Oneclass New", "oneclass123")

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
