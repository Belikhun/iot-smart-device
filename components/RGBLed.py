
from machine import Pin, PWM
import uasyncio as asyncio

class RGBLed:
	def __init__(self, red_pin, green_pin, blue_pin):
		self.red = PWM(Pin(red_pin, Pin.OUT), freq=1000)
		self.green = PWM(Pin(green_pin, Pin.OUT), freq=1000)
		self.blue = PWM(Pin(blue_pin, Pin.OUT), freq=1000)
		self.off()

		# Set initial color to off
		self.current_color = (0, 0, 0)
		self.animation_playing = False
		self._animation_task = None

	def set_color_raw(self, red_val, green_val, blue_val):
		self.current_color = (red_val, green_val, blue_val)
		self.red.duty(red_val)
		self.green.duty(green_val)
		self.blue.duty(blue_val)

	def set_color(self, color_value):
		if isinstance(color_value, tuple) and len(color_value) == 3:
			# If the input is an RGB tuple
			if all(0 <= val < 256 for val in color_value):
				red_val = int(color_value[0] * 1023 / 255)
				green_val = int(color_value[1] * 1023 / 255)
				blue_val = int(color_value[2] * 1023 / 255)
				self.set_color_raw(red_val, green_val, blue_val)
			else:
				raise ValueError("RGB values must be between 0 and 255")
		elif isinstance(color_value, str) and color_value.startswith("#"):
			# If the input is a Hex string
			# Remove "#" and convert hex to RGB
			hex_color = color_value.lstrip("#")
			if len(hex_color) == 6:
				r = int(hex_color[0:2], 16)
				g = int(hex_color[2:4], 16)
				b = int(hex_color[4:6], 16)
				# Convert RGB (0-255) to PWM duty cycle (0-1023)
				self.set_color_raw(r * 4, g * 4, b * 4)
			else:
				raise ValueError("Invalid Hex color format")
		else:
			raise ValueError("color_value must be an RGB tuple or a Hex color string")

	def off(self):
		self.set_color_raw(0, 0, 0)

	def deinit(self):
		self.red.deinit()
		self.green.deinit()
		self.blue.deinit()

	async def animate(self, animation_type, color=None, duration=0.5, interval=0.01):
		self.animation_playing = True

		if animation_type == "blink":
			while True:
				if not self.animation_playing:
					return

				# Set LED to the desired color
				self.set_color_raw(*color)
				await asyncio.sleep(duration)

				if not self.animation_playing:
					return

				# Turn off LED
				self.off()
				await asyncio.sleep(duration)
		
		elif animation_type == "breathe":
			max_brightness = 1023
			min_brightness = 0
			
			while True:
				if not self.animation_playing:
					return

				# Fade in
				for duty in range(min_brightness, max_brightness + 1, 20):
					self.set_color_raw(int(duty * color[0] / max_brightness), 
									int(duty * color[1] / max_brightness), 
									int(duty * color[2] / max_brightness))

					await asyncio.sleep(interval)

					if not self.animation_playing:
						return

				# Fade out
				for duty in range(max_brightness, min_brightness - 1, -20):
					self.set_color_raw(int(duty * color[0] / max_brightness), 
									int(duty * color[1] / max_brightness), 
									int(duty * color[2] / max_brightness))

					await asyncio.sleep(interval)

					if not self.animation_playing:
						return

	def start_animation(self, animation_type, color=None, duration=0.5, interval=0.01):
		if color is None:
			color = self.current_color
		
		# Stop any currently running animation
		self.stop_animation()

		# Start the animation in a new task
		self._animation_task = asyncio.create_task(self.animate(animation_type, color, duration, interval))

	def stop_animation(self):
		if self._animation_task:
			self._animation_task.cancel()  # Cancel the running animation task
			self._animation_task = None

		self.set_color_raw(*self.current_color)
		self.animation_playing = False
