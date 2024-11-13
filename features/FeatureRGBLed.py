from features import FeatureBase
from components import RGBLed

class FeatureRGBLed(FeatureBase):
	def __init__(self, id: str, name: str, red_pin: int, green_pin: int, blue_pin: int):
		super(FeatureRGBLed, self).__init__(id, name)
		self.component = RGBLed(red_pin, green_pin, blue_pin)

	def process_value(self, new_value):
		if (isinstance(new_value, list)):
			new_value = tuple(new_value)

		return new_value

	def do_update_component(self):
		self.component.set_color(self.get_value())
