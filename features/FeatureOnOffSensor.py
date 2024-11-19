from features import FeatureBase
from features.utils import FeatureUpdateSource
from components import OnOffSensor

class FeatureOnOffSensor(FeatureBase):
	def __init__(self, id: str, name: str, pin: int, flip: bool = False):
		super(FeatureOnOffSensor, self).__init__(id, name, flags=FeatureBase.FLAG_READ)
		self.component = OnOffSensor(pin, flip)
		self.component.set_on_high(self.on_high)
		self.component.set_on_low(self.on_low)
		self.current_value = self.component.get_state()

	def on_high(self):
		self.set_value(True, update_source=FeatureUpdateSource.HARDWARE)	

	def on_low(self):
		self.set_value(False, update_source=FeatureUpdateSource.HARDWARE)	
