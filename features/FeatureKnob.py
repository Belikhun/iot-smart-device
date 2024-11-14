from features import FeatureBase
from features.utils import FeatureUpdateSource
from components import RotaryEncoder

class FeatureKnob(FeatureBase):
	def __init__(self, id: str, name: str, pin_clk: int, pin_dt: int, min: int = 0, max: int = 100, step: int = 1, default: int = 0):
		super(FeatureKnob, self).__init__(id, name)

		self.min = min
		self.max = max
		self.step = step

		self.component = RotaryEncoder(pin_clk, pin_dt)
		self.component.on_rotate(self.handle_rotate)
		self.current_value = default

	def handle_rotate(self, direction):
		value = self.get_value()

		if direction == RotaryEncoder.CW:
			value += self.step
		elif direction == RotaryEncoder.CCW:
			value -= self.step

		value = min(self.max, max(self.min, value))

		if (self.get_value() == value):
			return

		self.set_value(value, update_source=FeatureUpdateSource.HARDWARE)
