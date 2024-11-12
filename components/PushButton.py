from machine import Pin
import uasyncio as asyncio
import time

class PushButton:
	def __init__(self, pin: int, debounce_ms=50):
		self.pin = Pin(pin, Pin.IN)  # No internal pull resistors
		self.debounce_ms = debounce_ms
		self._last_state = self.pin.value()
		self._last_time = time.ticks_ms()
		self.on_press = None
		self.on_release = None

	async def listen(self):
		while True:
			current_state = self.pin.value()
			current_time = time.ticks_ms()

			# Debounce logic
			if current_state != self._last_state:
				if time.ticks_diff(current_time, self._last_time) > self.debounce_ms:
					self._last_time = current_time
					if current_state == 1 and self.on_press:
						self.on_press()
					elif current_state == 0 and self.on_release:
						self.on_release()
				self._last_state = current_state

			await asyncio.sleep_ms(50)

	def start_listen(self):
		asyncio.create_task(self.listen())

	def set_on_press(self, callback):
		self.on_press = callback

	def set_on_release(self, callback):
		self.on_release = callback
