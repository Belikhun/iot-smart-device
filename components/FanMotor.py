import machine

class FanMotor:
	def __init__(self, pin_ina: int, pin_inb: int, pwm_frequency=1000):
		self.ina = machine.PWM(machine.Pin(pin_ina, machine.Pin.OUT))
		self.inb = machine.PWM(machine.Pin(pin_inb, machine.Pin.OUT))
		
		self.ina.freq(pwm_frequency)
		self.inb.freq(pwm_frequency)
		
		self.stop()

	def set_speed(self, speed):
		if speed > 1.0 or speed < -1.0:
			raise ValueError("Speed must be between -1.0 and 1.0")

		duty_cycle = int(abs(speed) * 1023)

		if speed > 0:
			self.ina.duty(duty_cycle)
			self.inb.duty(0)
		elif speed < 0:
			self.ina.duty(0)
			self.inb.duty(duty_cycle)
		else:
			self.stop()

	def stop(self):
		self.ina.duty(0)
		self.inb.duty(0)

	def brake(self):
		self.ina.duty(1023)
		self.inb.duty(1023)
