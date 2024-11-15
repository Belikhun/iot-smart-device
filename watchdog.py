import gc
import machine
import esp32
import uasyncio as asyncio
from logger import scope
import time
import client

log = scope("watchdog")
MONITOR_WS = False
LAST_WS_HEARTBEAT = 0

async def watchdog_loop():
	global MONITOR_WS, LAST_WS_HEARTBEAT
	gc.enable()

	while True:
		try:
			cleaned = gc.collect()

			if cleaned:
				log("INFO", f"Collected and cleaned {cleaned} dangling objects")

			timestamp = int(time.time_ns() / 1000000)
			temp = (esp32.raw_temperature() - 32.0) / 1.8
			log("DEBG", "TIME: {}".format(timestamp))
			log("DEBG", " CPU: freq {}, temp {:5.1f}C".format(machine.freq(), temp))

			if (MONITOR_WS):
				heartbeat = timestamp - LAST_WS_HEARTBEAT
				log("DEBG", "  WS: d_heartbeat={}".format(heartbeat))

				if (heartbeat > 10000):
					log("WARN", "Websocket lost heartbeat for more than 10 seconds, will attempt to reconnect now")
					await client.ws_stop_loop()
					client.ws_do_reconnect()
		except Exception as e:
			log("WARN", f"Watchdog crashed with error: {e}")

		await asyncio.sleep(5)

def start_watchdog():
	asyncio.create_task(watchdog_loop())

def start_monitor_ws():
	global MONITOR_WS, LAST_WS_HEARTBEAT
	MONITOR_WS = True
	LAST_WS_HEARTBEAT = int(time.time_ns() / 1000000)
	log("DEBG", f"Websocket heartbeat monitoring started @ {LAST_WS_HEARTBEAT}")

def stop_monitor_ws():
	global MONITOR_WS
	MONITOR_WS = False
	log("DEBG", f"Websocket heartbeat monitoring stopped @ {LAST_WS_HEARTBEAT}")

def ws_heartbeat():
	global MONITOR_WS, LAST_WS_HEARTBEAT

	if not MONITOR_WS:
		return

	LAST_WS_HEARTBEAT = int(time.time_ns() / 1000000)
