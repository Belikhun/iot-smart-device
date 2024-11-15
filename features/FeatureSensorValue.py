from features import FeatureBase

class FeatureSensorValue(FeatureBase):
	def __init__(self, id: str, name: str, unit: str = None):
		super(FeatureSensorValue, self).__init__(id, name, flags=FeatureBase.FLAG_READ)
		self.unit = unit
		self.current_value = 0

	def process_value(self, new_value):
		if (new_value is None):
			return 0

		return new_value

	def get_describe_data(self):
		data = super().get_describe_data()
		data["unit"] = self.unit
		return data
