from features import FeatureBase

class FeatureHumidity(FeatureBase):
	def __init__(self, id: str, name: str):
		super(FeatureHumidity, self).__init__(id, name)
		self.current_value = 0
