from wsc import WebsocketClient
from logger import scope
import asyncio

log = scope("ws")
WS_CLIENT = WebsocketClient()
WS_TASK = None

async def ws_connect(server):
	try:
		log("INFO", f"Handshaking to {server}")
		
		if not await WS_CLIENT.handshake(server):
			log("WARN", "Handshake to server failed")
			return False

		log("OKAY", "Handshake successfully")
		return True
	except Exception as e:
		log("WARN", f"Handshake failed with error: {e}")
		return False

async def ws_loop():
	mes_count = 0
	data = []
	lock = asyncio.Lock()

	while await WS_CLIENT.open():
		data = await WS_CLIENT.recv()
		print("Data: " + str(data) + "; " + str(mes_count))
		# close socket for every 10 messages (even ping/pong)
		if mes_count == 10:
			await WS_CLIENT.close()
			print("ws is open: " + str(await WS_CLIENT.open()))
		mes_count += 1

		if data is not None:
			await lock.acquire()
			data.append(data)
			lock.release()

		await asyncio.sleep_ms(50)

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
