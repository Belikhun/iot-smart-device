import machine
import uasyncio as asyncio
from logger import scope

log = scope("buzzer")

class Buzzer:
	def __init__(self, pin: int, frequency=1000):
		self.pin = machine.Pin(pin, machine.Pin.OUT)
		self.frequency = frequency
		self.buzzer = machine.PWM(self.pin, freq=frequency, duty=0)
		self.is_playing = False
		self.task = None
		self.duty = 512
		self.lock = asyncio.Lock()

	def play_tone(self, frequency=None):
		if frequency:
			self.frequency = frequency

		if self.frequency == 0:
			self.stop_tone()
			return
			# self.stop_tone()

		# self.buzzer.init(freq=self.frequency, duty=self.duty)
		self.buzzer.freq(self.frequency)
		self.buzzer.duty(self.duty)
		self.is_playing = True

	def stop_tone(self, stop_task=False):
		log("DEBG", "STOP")

		if self.is_playing:
			self.buzzer.duty(0)
			# self.buzzer.deinit()

		self.is_playing = False

		if (stop_task and self.task):
			self.task.cancel()

	async def beep(self, duration=0.2, frequency=None):
		log("DEBG", f"BEEP duration={duration} freq={frequency}")
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

	async def play_melody(self, notes, tempo=0.5, loop=False):
		log("DEBG", f"PLAY tempo={tempo} loop={loop}")

		while True:
			for note in notes:
				if note > 0:
					self.play_tone(note)
					await asyncio.sleep(tempo * 0.9)
					self.stop_tone()
					await asyncio.sleep(tempo * 0.1)
				else:
					self.stop_tone()
					await asyncio.sleep(tempo)

			if not loop:
				break

		self.stop_tone()

	def do_play_melody(self, notes, tempo=0.5, loop=False):
		if self.task:
			self.task.cancel()
			self.task = None

		self.task = asyncio.create_task(self.play_melody(notes, tempo, loop))
