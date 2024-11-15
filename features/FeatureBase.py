from utils import hw_id
from logger import scope
from features.utils import FeatureUpdateSource, register_feature, push_feature_value
from micropython import const

class FeatureBase:
	FLAG_READ = const(1)

	FLAG_WRITE = const(2)

	def __init__(self, id: str, name: str, flags: int = FLAG_READ | FLAG_WRITE):
		self.id = id
		self.uuid = f"{hw_id()}/{id}"
		self.name = name
		self.current_value = None
		self.update_handler = None
		self.component = None
		self.flags = flags
		self.log = scope(f"feature:{self.id}")
		self.init()

		register_feature(self)

	def init(self):
		pass

	def value(self, new_value=None):
		if new_value is not None:
			self.set_value(new_value)

		return self.get_value()

	def set_value(self, new_value, update_source=FeatureUpdateSource.INTERNAL):
		self.current_value = self.process_value(new_value)
		self.log("INFO", f"value={str(new_value)} src={update_source}")

		if (self.update_handler):
			self.update_handler(self)

		if (update_source != FeatureUpdateSource.HARDWARE):
			self.log("DEBG", "Will perform component update")
			self.do_update_component()

		if (update_source != FeatureUpdateSource.SERVER):
			self.log("DEBG", "Will push value to server")
			self.do_push_value()

	def process_value(self, new_value):
		return new_value

	def get_value(self):
		return self.current_value

	def on_update(self, callback: callable):
		self.update_handler = callback

	def do_update_component(self):
		pass

	def do_push_value(self):
		push_feature_value(self)

	def get_describe_data(self):
		return {
			"id": self.id,
			"uuid": self.uuid,
			"name": self.name,
			"kind": self.__class__.__name__,
			"flags": self.flags
		}

	def get_update_data(self):
		return {
			"id": self.id,
			"uuid": self.uuid,
			"value": self.get_value()
		}
