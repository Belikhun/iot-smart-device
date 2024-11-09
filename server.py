import uasyncio as asyncio
from ahttpserver import HTTPResponse, HTTPServer, sendfile
from logger import scope

log = scope("http:server")
server = HTTPServer()

@server.route("GET", "/")
async def index(reader, writer, request):
	response = HTTPResponse(200, "text/html", close=True)
	await response.send(writer)
	await sendfile(writer, "public/index.html")

@server.route("GET", "/generate_204")
async def android_portal_check(reader, writer, request):
	response = HTTPResponse(301, "text/html", True, {
		"Location": "http://device.local/"
	})

	await response.send(writer)

def start_server():
	log("INFO", "Starting configuration portal http server...")
	asyncio.create_task(server.start())
	log("OKAY", "Configuration portal http server started")

def stop_server():
	log("INFO", "Stopping configuration portal http server...")
	server.stop()
	log("INFO", "Stopped configuration portal http server")
