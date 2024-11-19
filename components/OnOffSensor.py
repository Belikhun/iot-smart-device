from machine import Pin
import time

class OnOffSensor:
	def __init__(self, pin_num, flip: bool = False, debounce_ms: int = 50):
		self.pin = Pin(pin_num, Pin.IN)
		self.debounce_ms = debounce_ms
		self._last_time = 0
		self.state = (not self.pin.value()) if flip else (self.pin.value())

		self.on_high = None
		self.on_low = None
		self.flip = flip

		self.pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._handle_interrupt)

	def _handle_interrupt(self, pin):
		current_time = time.ticks_ms()
		if time.ticks_diff(current_time, self._last_time) < self.debounce_ms:
			return

		self._last_time = current_time
		new_state = (not self.pin.value()) if self.flip else (self.pin.value())

		if new_state != self.state:
			self.state = new_state

			if new_state == 1 and self.on_high:
				self.on_high()
			elif new_state == 0 and self.on_low:
				self.on_low()

	def get_state(self) -> bool:
		return self.state == 1

	def set_on_high(self, callback):
		self.on_high = callback

	def set_on_low(self, callback):
		self.on_low = callback
