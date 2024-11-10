import uasyncio as asyncio
from ahttpserver import HTTPResponse, HTTPServer, sendfile
from logger import scope
import json
import ubinascii
from config import config
from wifi import get_wifi_status, get_wifi_if

log = scope("http:server")
server = HTTPServer()

@server.route("GET", "/")
async def index(reader, writer, request):
	response = HTTPResponse(200, "text/html", close=True)
	await response.send(writer)
	await sendfile(writer, "public/index.html")

@server.route("GET", "/api/wifi/status")
async def wifi_status(reader, writer, request):
	interface = get_wifi_if()
	mac = ubinascii.hexlify(interface.config("mac")).decode("utf-8")
	mac = ":".join(mac[i:i+2] for i in range(0, len(mac), 2))

	response_body = json.dumps({
		"status": get_wifi_status(),
		"mac": mac,
		"ssid": interface.config("ssid"),
		"password": config("password"),
		"rssi": interface.status("rssi"),
		"channel": interface.config("channel"),
		"txpower": interface.config("txpower")
	})

	response = HTTPResponse(200, "application/json", close=True, header={
		"Content-Length": str(len(response_body))
	})

	await response.send(writer)
	writer.write(response_body)
	await writer.drain()

@server.route("GET", "/api/wifi/scan")
async def scan_wifi(reader, writer, request):
	interface = get_wifi_if()
	scan_result = interface.scan()
	sec_values = ["OPEN", "WEP", "WPA-PSK", "WPA2-PSK", "WPA/WPA2-PSK"]
	scan_data = []

	for scan_item in scan_result:
		if (scan_item[0] == ""):
			continue

		bssid = ubinascii.hexlify(scan_item[1]).decode("utf-8")
		bssid = ":".join(bssid[i:i+2] for i in range(0, len(bssid), 2))

		scan_data.append({
			"ssid": scan_item[0],
			"bssid": bssid,
			"channel": scan_item[2],
			"rssi": scan_item[3],
			"security": sec_values[scan_item[4]],
			"hidden": bool(scan_item[5])
		})

	response_body = json.dumps(scan_data)

	response = HTTPResponse(200, "application/json", close=True, header={
		"Content-Length": str(len(response_body))
	})

	await response.send(writer)
	writer.write(response_body)
	await writer.drain()

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
