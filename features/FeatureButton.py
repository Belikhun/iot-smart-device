from features import FeatureBase
from features.utils import FeatureUpdateSource
from components import PushButton

class FeatureButton(FeatureBase):
	def __init__(self, id: str, name: str, pin: int, default: bool = False):
		super(FeatureButton, self).__init__(id, name)
		self.component = PushButton(pin)
		self.component.set_on_release(self.handle_button)
		self.current_value = default

	def handle_button(self):
		self.set_value(not self.get_value(), update_source=FeatureUpdateSource.HARDWARE)
