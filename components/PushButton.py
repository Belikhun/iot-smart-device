from machine import Pin
import time

class PushButton:
	def __init__(self, pin: int, debounce_ms=50):
		self.pin = Pin(pin, Pin.IN)
		self.debounce_ms = debounce_ms
		self._last_state = self.pin.value()
		self._last_time = time.ticks_ms()
		self.on_press = None
		self.on_release = None

		self.pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._handle_interrupt)

	def _handle_interrupt(self, pin):
		current_time = time.ticks_ms()
		if time.ticks_diff(current_time, self._last_time) < self.debounce_ms:
			return

		self._last_time = current_time
		new_state = pin.value()

		if new_state != self._last_state:
			self._last_state = new_state

			if new_state == 1 and self.on_press:
				self.on_press()
			elif new_state == 0 and self.on_release:
				self.on_release()

	def set_on_press(self, callback):
		self.on_press = callback

	def set_on_release(self, callback):
		self.on_release = callback

	@property
	def state(self):
		return self._last_state
