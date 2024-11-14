import machine
import uasyncio as asyncio

class Buzzer:
	def __init__(self, pin: int, frequency=1000):
		self.pin = pin
		self.frequency = frequency
		self.buzzer = machine.PWM(machine.Pin(pin))
		self.buzzer.deinit()
		self.is_playing = False
		self.task = None
		self.lock = asyncio.Lock()

	def play_tone(self, frequency=None):
		if frequency:
			self.frequency = frequency

		self.buzzer.init(freq=self.frequency, duty=512)
		self.is_playing = True

	def stop_tone(self, stop_task=False):
		self.buzzer.deinit()
		self.is_playing = False

		if (stop_task and self.task):
			self.task.cancel()

	async def beep(self, duration=0.2, frequency=None):
		await self.lock.acquire()
		self.play_tone(frequency)
		await asyncio.sleep(duration)
		self.stop_tone()
		self.lock.release()

	def do_beep(self, duration=0.2, frequency=None):
		if self.task:
			self.task.cancel()
			self.task = None

		self.task = asyncio.create_task(self.beep(duration, frequency))

	async def play_melody(self, notes, tempo=0.5):
		for note in notes:
			if note > 0:
				self.play_tone(note)
			else:
				self.stop_tone()

			await asyncio.sleep(tempo)

		self.stop_tone()

	def do_play_melody(self, notes, tempo=0.5):
		if self.task:
			self.task.cancel()
			self.task = None

		self.task = asyncio.create_task(self.play_melody(notes, tempo))
