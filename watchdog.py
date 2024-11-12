import gc
import machine
import esp32
import uasyncio as asyncio
from logger import scope

log = scope("watchdog")

async def watchdog_loop():
	gc.enable()

	while True:
		cleaned = gc.collect()

		if cleaned:
			log("INFO", f"Collected and cleaned {cleaned} dangling objects")

		temp = (esp32.raw_temperature() - 32.0) / 1.8
		log("DEBG", "CPU: freq {}, temp {:5.1f}C".format(machine.freq(), temp))
		await asyncio.sleep(10)

def start_watchdog():
	asyncio.create_task(watchdog_loop())
