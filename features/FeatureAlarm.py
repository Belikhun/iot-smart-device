from features import FeatureBase
from features.utils import FeatureUpdateSource
from components import Buzzer

class FeatureAlarm(FeatureBase):
	def __init__(self, id: str, name: str, pin: int):
		super(FeatureAlarm, self).__init__(id, name, flags=FeatureBase.FLAG_WRITE)
		self.component = Buzzer(pin)
		self.current_value = "off"

	async def do_update_component(self):
		value = self.get_value()

		if value == "off" or not isinstance(value, dict):
			self.component.stop_tone(stop_task=True)
			return

		action = value.get("action")
		data = value.get("data")

		if action == "beep":
			duration, freq = data
			await self.component.beep(duration, freq)
			self.set_value("off", FeatureUpdateSource.HARDWARE)
		elif action == "alert":
			alert_tone = [1500, 1500, 1500, 0]
			await self.component.play_melody(alert_tone, 0.2)
			self.set_value("off", FeatureUpdateSource.HARDWARE)
		elif action == "alarm":
			alarm_tone = [1200, 1500, 1200, 1500]
			self.component.do_play_melody(alarm_tone, 0.2, loop=True)
		else:
			self.component.stop_tone(stop_task=True)
