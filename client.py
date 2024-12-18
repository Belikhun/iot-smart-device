from wsc import WebsocketClient
from logger import scope
from utils import status_led, status_buzz
import uasyncio as asyncio
import watchdog
import time
import json

log = scope("ws")
WS_CLIENT = WebsocketClient()
WS_TASK = None
WS_URL = None
WS_SHOULD_DO_RECONNECT = True
WS_RECONNECT_TASK = None
WS_CONNECTED_HANDLER = None
WS_DATA_HANDLERS = []

def get_ws():
	global WS_CLIENT
	return WS_CLIENT

def ws_is_connected():
	global WS_CLIENT
	return WS_CLIENT.is_open()

async def ws_connect(url, reconnect=False, reconnect_delay=2):
	global WS_CLIENT, WS_URL, WS_TASK

	WS_URL = url

	try:
		status_led().stop_animation()
		await asyncio.sleep_ms(50)
		status_led().set_color((0, 0, 255))
		status_buzz().stop_tone(stop_task=True)

		if ws_is_connected():
			log("INFO", f"Stopping current websocket connection...")
			await WS_CLIENT.open(False)

		if WS_TASK:
			await ws_stop_loop()

		log("INFO", f"Handshaking to {url}")
		await status_buzz().beep(duration=0.1, frequency=726)

		if not await WS_CLIENT.handshake(url):
			log("WARN", "Handshake to server failed")
			status_led().start_animation("breathe", color=(0, 0, 255))
			status_buzz().do_beep(duration=0.2, frequency=820)

			if reconnect:
				ws_do_reconnect(reconnect_delay)

			return False

		tries = 0

		while not await WS_CLIENT.open():
			tries += 1

			if (tries > 10):
				log("WARN", "Handshake to server failed")
				status_led().start_animation("breathe", color=(0, 0, 255))
				status_buzz().do_beep(duration=0.2, frequency=820)

				if reconnect:
					ws_do_reconnect(reconnect_delay)

				return False

			log("INFO", f"Waiting until socket is fully connected... ({tries}/10)")
			await asyncio.sleep(1)

		log("OKAY", "Handshake successfully")
		status_led().start_animation("blink", (0, 255, 0))
		return True

	except Exception as e:
		log("WARN", f"Handshake failed with error: {e}")
		status_led().start_animation("breathe", color=(0, 255, 0))
		status_buzz().do_beep(duration=0.2, frequency=820)

		if reconnect:
			ws_do_reconnect(reconnect_delay)

		return False

async def ws_loop():
	global WS_CLIENT

	lock = asyncio.Lock()

	try:
		while await WS_CLIENT.open():
			data = await WS_CLIENT.recv()

			if data is not None:
				await lock.acquire()
				ws_handle_data(data)
				lock.release()

			await asyncio.sleep_ms(50)
	except Exception as e:
		log("WARN", f"Websocket RECV errored: {e}")

		if lock.locked():
			lock.release()

		status_buzz().do_beep(duration=0.2, frequency=820)
		ws_do_reconnect()

async def ws_start_loop():
	global WS_TASK, WS_CONNECTED_HANDLER

	if WS_TASK:
		await ws_stop_loop()

	log("INFO", "Starting websocket loop task...")
	status_led().set_color((0, 255, 0))
	WS_TASK = asyncio.create_task(ws_loop())
	watchdog.start_monitor_ws()
	await asyncio.sleep(1)

	log("INFO", "Executing websocket connected handler...")
	if WS_CONNECTED_HANDLER:
		WS_CONNECTED_HANDLER()

	status_buzz().do_play_melody([523, 659, 784, 1042, 0], 0.15)

async def ws_stop_loop():
	global WS_TASK, WS_CLIENT

	if WS_TASK:
		log("INFO", "Stopping websocket loop task")
		WS_TASK.cancel()
		WS_TASK = None
		await WS_CLIENT.close()
		watchdog.stop_monitor_ws()

async def ws_reconnect(delay=2):
	global WS_URL, WS_SHOULD_DO_RECONNECT

	if not WS_SHOULD_DO_RECONNECT:
		return

	log("INFO", f"Auto re-connect to {WS_URL} in {delay} seconds")
	await asyncio.sleep(delay)

	if await ws_connect(WS_URL, reconnect=True, reconnect_delay=delay):
		await ws_start_loop()

def ws_do_reconnect(delay=2):
	global WS_SHOULD_DO_RECONNECT, WS_RECONNECT_TASK
	WS_SHOULD_DO_RECONNECT = True
	WS_RECONNECT_TASK = asyncio.create_task(ws_reconnect(delay))

def ws_stop_reconnect_retry():
	global WS_SHOULD_DO_RECONNECT, WS_RECONNECT_TASK
	WS_SHOULD_DO_RECONNECT = False

	if WS_RECONNECT_TASK:
		WS_RECONNECT_TASK.cancel()
		WS_RECONNECT_TASK = None

	log("INFO", f"Auto re-connect stopped")

async def ws_send(command, data=None, source="system"):
	global WS_CLIENT

	timestamp = int(time.time_ns() / 1000000)
	payload = {
		"command": command,
		"source": source,
		"data": data,
		"timestamp": int(time.time_ns() / 1000000)
	}

	log("INFO", f"CMD[@{timestamp}] {source} -> {command}")

	if await WS_CLIENT.send(json.dumps(payload)):
		log("OKAY", f"CMD[@{timestamp}] SENT")
	else:
		log("WARN", f"CMD[@{timestamp}] FAILED")

def ws_do_send(command, data=None, source="system"):
	asyncio.create_task(ws_send(command, data, source))

def ws_on_data(callable: callable):
	global WS_DATA_HANDLERS
	log("INFO", "Websocket data handler registered")
	WS_DATA_HANDLERS.append(callable)

def ws_on_connected(callable: callable):
	global WS_CONNECTED_HANDLER
	log("INFO", "Websocket connected handler registered")
	WS_CONNECTED_HANDLER = callable

def ws_handle_data(recv_data: str):
	global WS_DATA_HANDLERS

	try:
		data: dict = json.loads(recv_data)

		for handler in WS_DATA_HANDLERS:
			if handler(data):
				break

			# Cycle to the next handler.
			continue

	except Exception as e:
		log("WARN", f"Malformed websocket recv data: {e}")
