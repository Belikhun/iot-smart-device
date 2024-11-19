from features import FeatureBase
from components import OnOffToggle

class FeatureOnOffToggle(FeatureBase):
	def __init__(self, id: str, name: str, pin: int, flip: bool = False, default: bool = False):
		super(FeatureOnOffToggle, self).__init__(id, name, flags=FeatureBase.FLAG_WRITE)
		self.component = OnOffToggle(pin, flip=flip, default=default)
		self.current_value = default

	def do_update_component(self):
		self.component.set(self.get_value())
