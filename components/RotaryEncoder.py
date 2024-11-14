from machine import Pin
import time

class RotaryEncoder:
	CW = 1
	CCW = -1

	def __init__(self, pin_clk: int, pin_dt: int):
		# Initialize pins
		self.pin_clk = Pin(pin_clk, Pin.IN)
		self.pin_dt = Pin(pin_dt, Pin.IN)

		# Initial state
		self.last_state = self.pin_clk.value()
		self.rotate_handlers = []
		self.last_handle = time.ticks_ms()

		# Add interrupts to handle rotation
		self.pin_clk.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._handle_interrupt)
		self.pin_dt.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._handle_interrupt)

	def _handle_interrupt(self, pin):
		self._update()

	def _update(self):
		# Read the new states
		current_state = self.pin_clk.value()
		pin_dt_state = self.pin_dt.value()

		# Check direction and update position
		if current_state != self.last_state:  # A change in state detected
			if pin_dt_state != current_state:
				self.handle_rotate(RotaryEncoder.CW)
			else:
				self.handle_rotate(RotaryEncoder.CCW)

			# Update last state
			self.last_state = current_state

	def handle_rotate(self, direction):
		current_time = time.ticks_ms()

		if (current_time - self.last_handle > 100):
			self.last_handle = current_time
			return

		self.last_handle = current_time - 100

		for handler in self.rotate_handlers:
			handler(direction)

	def on_rotate(self, handler: callable):
		self.rotate_handlers.append(handler)
