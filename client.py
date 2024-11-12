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

def get_ws():
	global WS_CLIENT
	return WS_CLIENT

async def ws_connect(url, reconnect=False):
	global WS_CLIENT, WS_URL

	WS_URL = url

	try:
		status_led().stop_animation()
		await asyncio.sleep_ms(50)
		status_led().set_color((0, 0, 255))
		status_buzz().stop_tone()
		log("INFO", f"Handshaking to {url}")
		await asyncio.sleep_ms(500)

		if not await WS_CLIENT.handshake(url):
			log("WARN", "Handshake to server failed")
			status_led().start_animation("blink", (255, 0, 0), duration=0.15)
			status_buzz().do_beep(duration=0.2, frequency=820)

			if reconnect:
				ws_do_reconnect()

			return False

		log("OKAY", "Handshake successfully")
		status_led().start_animation("blink", (0, 255, 0))
		return True
	except Exception as e:
		log("WARN", f"Handshake failed with error: {e}")
		status_led().start_animation("blink", (255, 0, 0), duration=0.15)
		status_buzz().do_beep(duration=0.2, frequency=820)

		if reconnect:
			ws_do_reconnect()

		return False

async def ws_loop():
	global WS_CLIENT

	recv = []
	lock = asyncio.Lock()

	try:
		while await WS_CLIENT.open():
			data = await WS_CLIENT.recv()

			if data is not None:
				log("DEBG", f"Data: {data}")
				await lock.acquire()
				recv.append(data)
				lock.release()

			await asyncio.sleep_ms(50)
	except Exception as e:
		log("WARN", f"Websocket RECV errored: {e}")

		if lock.locked():
			lock.release()

		status_buzz().do_beep(duration=0.2, frequency=820)
		ws_do_reconnect()

def ws_start_loop():
	global WS_TASK

	if WS_TASK:
		ws_stop_loop()

	log("INFO", "Starting websocket loop task")
	asyncio.create_task(ws_loop())

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
		status_buzz().do_play_melody([523, 659, 784, 1042, 0], 0.15)

def ws_do_reconnect(delay=2):
	asyncio.create_task(ws_reconnect(delay))

async def ws_send(command, data):
	global WS_CLIENT

	timestamp = int(time.time_ns() / 1000000)
	payload = {
		"command": command,
		"data": data,
		"timestamp": int(time.time_ns() / 1000000)
	}

	log("INFO", f"CMD[@{timestamp}] {command}")

	if await WS_CLIENT.send(json.dumps(payload)):
		log("OKAY", f"CMD[@{timestamp}] SENT")
	else:
		log("WARN", f"CMD[@{timestamp}] FAILED")

def ws_do_send(command, data):
	asyncio.create_task(ws_send(command, data))
