from wsc import WebsocketClient
from logger import scope
from utils import status_led, status_buzz
import uasyncio as asyncio
import time
import json

log = scope("ws")
WS_CLIENT = WebsocketClient()
WS_TASK = None
WS_URL = None
WS_CONNECTED_HANDLER = None
WS_DATA_HANDLER = None

def get_ws():
	global WS_CLIENT
	return WS_CLIENT

def ws_is_connected():
	global WS_CLIENT
	return WS_CLIENT.is_open()

async def ws_connect(url, reconnect=False):
	global WS_CLIENT, WS_URL

	WS_URL = url

	try:
		status_led().stop_animation()
		await asyncio.sleep_ms(50)
		status_led().set_color((0, 0, 255))
		status_buzz().stop_tone()

		if ws_is_connected():
			log("INFO", f"Stopping current websocket connection...")
			ws_stop_loop()
			await WS_CLIENT.open(False)

		log("INFO", f"Handshaking to {url}")
		await asyncio.sleep_ms(500)

		if not await WS_CLIENT.handshake(url):
			log("WARN", "Handshake to server failed")
			status_led().start_animation("breathe", color=(0, 0, 255))
			status_buzz().do_beep(duration=0.2, frequency=820)

			if reconnect:
				ws_do_reconnect()

			return False

		log("OKAY", "Handshake successfully")
		status_led().start_animation("blink", (0, 255, 0))
		return True
	except Exception as e:
		log("WARN", f"Handshake failed with error: {e}")
		status_led().start_animation("breathe", color=(0, 255, 0))
		status_buzz().do_beep(duration=0.2, frequency=820)

		if reconnect:
			ws_do_reconnect()

		return False

async def ws_loop():
	global WS_CLIENT

	lock = asyncio.Lock()

	try:
		while await WS_CLIENT.open():
			data = await WS_CLIENT.recv()

			if data is not None:
				ws_handle_data(data)

			await asyncio.sleep_ms(50)
	except Exception as e:
		log("WARN", f"Websocket RECV errored: {e}")

		if lock.locked():
			lock.release()

		status_buzz().do_beep(duration=0.2, frequency=820)
		ws_do_reconnect()

def ws_start_loop():
	global WS_TASK, WS_CONNECTED_HANDLER

	if WS_TASK:
		ws_stop_loop()

	log("INFO", "Starting websocket loop task")
	WS_TASK = asyncio.create_task(ws_loop())
	status_buzz().do_play_melody([523, 659, 784, 1042, 0], 0.15)

	if WS_CONNECTED_HANDLER:
		WS_CONNECTED_HANDLER()

def ws_stop_loop():
	global WS_TASK

	if WS_TASK:
		log("INFO", "Stopping websocket loop task")
		WS_TASK.cancel()
		WS_TASK = None	

async def ws_reconnect(delay=2):
	global WS_URL

	log("INFO", f"Auto re-connect to {WS_URL} in {delay} seconds")
	await asyncio.sleep(delay)

	if await ws_connect(WS_URL, reconnect=True):
		ws_start_loop()

def ws_do_reconnect(delay=2):
	asyncio.create_task(ws_reconnect(delay))

async def ws_send(command, data, source="system"):
	global WS_CLIENT

	timestamp = int(time.time_ns() / 1000000)
	payload = {
		"command": command,
		"source": source,
		"data": data,
		"timestamp": int(time.time_ns() / 1000000)
	}

	log("INFO", f"CMD[{source}@{timestamp}] {command}")

	if await WS_CLIENT.send(json.dumps(payload)):
		log("OKAY", f"CMD[{source}@{timestamp}] SENT")
	else:
		log("WARN", f"CMD[{source}@{timestamp}] FAILED")

def ws_do_send(command, data, source="system"):
	asyncio.create_task(ws_send(command, data, source))

def ws_on_data(callable: callable):
	global WS_DATA_HANDLER
	log("INFO", "Websocket data handler registered")
	WS_DATA_HANDLER = callable

def ws_on_connected(callable: callable):
	global WS_CONNECTED_HANDLER
	log("INFO", "Websocket websocket connected handler registered")
	WS_CONNECTED_HANDLER = callable

def ws_handle_data(recv_data: str):
	global WS_DATA_HANDLER

	try:
		data: dict = json.loads(recv_data)

		if (WS_DATA_HANDLER):
			WS_DATA_HANDLER(data)

	except Exception as e:
		log("WARN", f"Malformed websocket recv data: {e}")
