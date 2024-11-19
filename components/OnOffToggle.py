from machine import Pin

class OnOffToggle:
	def __init__(self, pin: int, flip: bool = False, default: bool = True):
		self.pin = Pin(pin, Pin.OUT)
		self.state = False
		self.flip = flip
		self.set(default)

	def set(self, state: bool):
		if (state):
			self.pin.off() if self.flip else self.pin.on()
			self.state = True
		else:
			self.pin.on() if self.flip else self.pin.off()
			self.state = False

	def toggle(self):
		self.set(not self.state)

	def on(self):
		self.set(True)

	def off(self):
		self.set(False)
