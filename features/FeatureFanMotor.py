from features import FeatureBase
from components import FanMotor

class FeatureFanMotor(FeatureBase):
	def __init__(self, id: str, name: str, pin_a: int, pin_b: int):
		super(FeatureFanMotor, self).__init__(id, name, flags=FeatureBase.FLAG_WRITE)

		self.component = FanMotor(pin_a, pin_b)
		self.current_value = 0

	def do_update_component(self):
		value = self.get_value()
		self.component.set_speed(value / 100)

	def get_describe_data(self):
		data = super().get_describe_data()
		data["min"] = -100
		data["max"] = 100
		return data
