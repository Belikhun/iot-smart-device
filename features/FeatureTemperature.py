from features import FeatureBase

class FeatureTemperature(FeatureBase):
	def __init__(self, id: str, name: str):
		super(FeatureTemperature, self).__init__(id, name)
		self.current_value = 0

	def process_value(self, new_value):
		if (new_value is None):
			return 0

		return new_value
