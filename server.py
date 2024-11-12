import uasyncio as asyncio
from ahttpserver import HTTPRequest, HTTPResponse, HTTPServer, sendfile
from logger import scope, get_logs
import json
import ubinascii
from config import config, set_config
from utils import send_response_in_chunks
from wifi import get_wifi_status, get_wifi_if, connect_wifi
from utils import hw_id
from client import ws_is_connected, ws_connect, ws_start_loop

log = scope("http:server")
server = HTTPServer()
portal_opened = False

def is_portal_opened():
	global portal_opened
	return portal_opened

@server.route("GET", "/")
async def index(reader, writer, request: HTTPRequest):
	global portal_opened
	portal_opened = True

	response = HTTPResponse(200, "text/html", close=True)
	await response.send(writer)
	await sendfile(writer, "public/index.html")

@server.route("GET", "/api/info")
async def hw_info(reader, writer, request: HTTPRequest):
	response_data = {
		"hwid": hw_id(),
		"name": config("name")
	}

	response_body = json.dumps(response_data).encode("utf-8")

	response = HTTPResponse(200, "application/json", close=True, header={
		"Content-Length": str(len(response_body))
	})

	await response.send(writer)
	await send_response_in_chunks(writer, response_body)

@server.route("GET", "/api/wifi/status")
async def wifi_status(reader, writer, request: HTTPRequest):
	interface = get_wifi_if()
	response_data = {}

	if not interface.isconnected():
		response_data = {
			"status": get_wifi_status()
		}
	else:
		mac = ubinascii.hexlify(interface.config("mac")).decode("utf-8")
		mac = ":".join(mac[i:i+2] for i in range(0, len(mac), 2))

		response_data = {
			"status": get_wifi_status(),
			"mac": mac,
			"ssid": interface.config("ssid"),
			"password": config("password"),
			"rssi": interface.status("rssi"),
			"channel": interface.config("channel"),
			"txpower": interface.config("txpower"),
			"address": interface.ifconfig()[0]
		}

	response_body = json.dumps(response_data).encode("utf-8")

	response = HTTPResponse(200, "application/json", close=True, header={
		"Content-Length": str(len(response_body))
	})

	await response.send(writer)
	await send_response_in_chunks(writer, response_body)

@server.route("GET", "/api/wifi/scan")
async def scan_wifi(reader, writer, request: HTTPRequest):
	interface = get_wifi_if()
	scan_result = interface.scan()
	sec_values = ["OPEN", "WEP", "WPA-PSK", "WPA2-PSK", "WPA/WPA2-PSK", "UNKN", "UNKN", "UNKN", "UNKN"]
	scan_data = []

	for scan_item in scan_result:
		ssid = scan_item[0].decode("utf-8")

		if (ssid == ""):
			continue

		bssid = ubinascii.hexlify(scan_item[1]).decode("utf-8")
		bssid = ":".join(bssid[i:i+2] for i in range(0, len(bssid), 2))

		scan_data.append({
			"ssid": ssid,
			"bssid": bssid,
			"channel": scan_item[2],
			"rssi": scan_item[3],
			"security": sec_values[scan_item[4]],
			"hidden": bool(scan_item[5])
		})

		# Only the first 15 results
		if len(scan_data) >= 15:
			break

	response_body = json.dumps(scan_data).encode("utf-8")

	response = HTTPResponse(200, "application/json", close=True, header={
		"Content-Length": str(len(response_body))
	})

	await response.send(writer)
	await send_response_in_chunks(writer, response_body)

@server.route("GET", "/api/wifi/connect")
async def connect_to_wifi(reader, writer, request: HTTPRequest):
	ssid = request.parameters.get("ssid")
	password = request.parameters.get("password")

	if not ssid:
		raise ValueError("Missing SSID")

	success = False

	try:
		success = await connect_wifi(ssid, password)
	except Exception:
		success = False

	response_data = {
		"success": success,
		"status": get_wifi_status()
	}

	response_body = json.dumps(response_data).encode("utf-8")

	response = HTTPResponse(200, "application/json", close=True, header={
		"Content-Length": str(len(response_body))
	})

	await response.send(writer)
	await send_response_in_chunks(writer, response_body)

@server.route("GET", "/api/server/status")
async def server_status(reader, writer, request: HTTPRequest):
	response_data = {
		"server": config("server"),
		"connected": ws_is_connected()
	}

	response_body = json.dumps(response_data).encode("utf-8")

	response = HTTPResponse(200, "application/json", close=True, header={
		"Content-Length": str(len(response_body))
	})

	await response.send(writer)
	await send_response_in_chunks(writer, response_body)

@server.route("GET", "/api/server/connect")
async def server_status(reader, writer, request: HTTPRequest):
	server = request.parameters.get("server")
	server_addr = "ws://{}/ws/device".format(server)
	connected = await ws_connect(server_addr, reconnect=False)

	if (connected):
		set_config("server", server, save=True)
		ws_start_loop()

	response_data = { "connected": connected }
	response_body = json.dumps(response_data).encode("utf-8")

	response = HTTPResponse(200, "application/json", close=True, header={
		"Content-Length": str(len(response_body))
	})

	await response.send(writer)
	await send_response_in_chunks(writer, response_body)

@server.route("GET", "/api/logs")
async def server_log(reader, writer, request: HTTPRequest):
	index = int(request.parameters.get("index", 0))
	response_body = json.dumps(get_logs(index)).encode("utf-8")

	response = HTTPResponse(200, "application/json", close=True, header={
		"Content-Length": str(len(response_body))
	})

	await response.send(writer)
	await send_response_in_chunks(writer, response_body)

@server.route("GET", "/generate_204")
async def android_portal_check(reader, writer, request: HTTPRequest):
	response = HTTPResponse(301, "text/html", True, {
		"Location": "http://device.local/"
	})

	await response.send(writer)

@server.route("GET", "/hotspot-detect.html")
async def ios_portal_check(reader, writer, request: HTTPRequest):
	response = HTTPResponse(302, "text/html", True, {
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
