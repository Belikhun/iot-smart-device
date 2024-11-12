from machine import Pin

class OnOffPin:
	def __init__(self, pin_number, default=True):
		self.pin = Pin(pin_number, Pin.OUT)
		self.state = False
		self.set(default)

	def set(self, state):
		if state:
			self.pin.on()
			self.state = True
		else:
			self.pin.off()
			self.state = False

	def toggle(self):
		self.set(not self.state)

	def on(self):
		self.set(True)

	def off(self):
		self.set(False)
