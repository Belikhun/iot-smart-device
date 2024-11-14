from features import FeatureBase

class FeatureTemperature(FeatureBase):
	def __init__(self, id: str, name: str):
		super(FeatureTemperature, self).__init__(id, name)
		self.current_value = 0
