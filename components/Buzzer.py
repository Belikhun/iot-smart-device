import machine
import uasyncio as asyncio

class Buzzer:
	def __init__(self, pin: int, frequency=1000):
		self.pin = pin
		self.frequency = frequency
		self.buzzer = machine.PWM(machine.Pin(pin))
		self.buzzer.deinit()
		self.is_playing = False

	def play_tone(self, frequency=None):
		if frequency:
			self.frequency = frequency

		self.buzzer.init(freq=self.frequency, duty=512)
		self.is_playing = True

	def stop_tone(self):
		self.buzzer.deinit()
		self.is_playing = False

	async def beep(self, duration=0.2, frequency=None):
		self.play_tone(frequency)
		await asyncio.sleep(duration)
		self.stop_tone()

	def do_beep(self, duration=0.2, frequency=None):
		asyncio.create_task(self.beep(duration, frequency))

	async def play_melody(self, notes, tempo=0.5):
		for note in notes:
			if note > 0:
				self.play_tone(note)
			else:
				self.stop_tone()
			await asyncio.sleep(tempo)

		self.stop_tone()

	def do_play_melody(self, notes, tempo=0.5):
		asyncio.create_task(self.play_melody(notes, tempo))
