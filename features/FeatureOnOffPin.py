from features import FeatureBase
from components import OnOffPin

class FeatureOnOffPin(FeatureBase):
	def __init__(self, id: str, name: str, pin: int, flip: bool = False, default: bool = False):
		super(FeatureOnOffPin, self).__init__(id, name)
		self.component = OnOffPin(pin, flip=flip, default=default)
		self.current_value = default

	def do_update_component(self):
		self.component.set(self.get_value())
