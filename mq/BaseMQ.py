from machine import Pin, ADC
from micropython import const
import math
import utime
from logger import scope
import uasyncio as asyncio

log = scope("mq")

class BaseMQ(object):
	MQ_SAMPLE_TIMES = const(5)

	MQ_SAMPLE_INTERVAL = const(2000)

	MQ_HEATING_PERIOD = const(60000)

	MQ_COOLING_PERIOD = const(90000)

	STRATEGY_FAST = const(1)

	STRATEGY_ACCURATE = const(2)

	def __init__(self, pinData, pinHeater=-1, boardResistance = 10, baseVoltage = 5.0, measuringStrategy = STRATEGY_ACCURATE):
		self._heater = False
		self._cooler = False
		self._ro = -1

		self._useSeparateHeater = False
		self._baseVoltage = baseVoltage

		self._lastMesurement = utime.ticks_ms()
		self._rsCache = None
		self.dataIsReliable = False
		self.pin = Pin(pinData)
		self.pinData = ADC(self.pin)
		self.measuringStrategy = measuringStrategy
		self._boardResistance = boardResistance
		if pinHeater != -1:
			self.useSeparateHeater = True
			self.pinHeater = Pin(pinHeater, Pin.OUTPUT)
			pass

	def getRoInCleanAir(self):
		raise NotImplementedError("Please Implement this method")

	async def calibrate(self, ro=-1):
		if ro == -1:
			ro = 0
			for i in range(0, BaseMQ.MQ_SAMPLE_TIMES + 1):
				log("INFO", f"Calibrating {i}/{BaseMQ.MQ_SAMPLE_TIMES}")
				ro += self.__calculateResistance__(self.pinData.read())
				await asyncio.sleep_ms(BaseMQ.MQ_SAMPLE_INTERVAL)
				pass

			ro = ro / (self.getRoInCleanAir() * BaseMQ.MQ_SAMPLE_TIMES)
			pass

		self._ro = ro
		self._stateCalibrate = True
		pass

	def heaterPwrHigh(self):
		if self._useSeparateHeater:
			self._pinHeater.on()
			pass
		self._heater = True
		self._prMillis = utime.ticks_ms()

	def heaterPwrLow(self):
		self._heater = True
		self._cooler = True
		self._prMillis = utime.ticks_ms()

	def heaterPwrOff(self):
		if self._useSeparateHeater:
			self._pinHeater.off()
			pass

		self._pinHeater(0)
		self._heater = False

	def __calculateResistance__(self, rawAdc):
		log("DEBG", f"RS raw_adc={rawAdc}")
		if rawAdc == 0:
			rawAdc = 1

		vrl = rawAdc * (self._baseVoltage / 1023)
		rsAir = (self._baseVoltage - vrl) / vrl * self._boardResistance
		return rsAir

	async def __readRs__(self):
		if self.measuringStrategy == BaseMQ.STRATEGY_ACCURATE :            
				rs = 0
				for _ in range(0, BaseMQ.MQ_SAMPLE_TIMES + 1): 
					rs += self.__calculateResistance__(self.pinData.read())
					await asyncio.sleep_ms(BaseMQ.MQ_SAMPLE_INTERVAL)

				rs = rs / BaseMQ.MQ_SAMPLE_TIMES
				self._rsCache = rs
				self.dataIsReliable = True
				self._lastMesurement = utime.ticks_ms()                            
				pass
		else:
			rs = self.__calculateResistance__(self.pinData.read())
			self.dataIsReliable = False
			pass

		return rs

	async def readScaled(self, a, b):
		ratio = await self.readRatio()
		if (ratio <= 0):
			ratio = 0.01

		return math.exp((math.log(ratio) - b) / a)

	async def readRatio(self):
		return (await self.__readRs__()) / self._ro

	def heatingCompleted(self):
		if (self._heater) and (not self._cooler) and (utime.ticks_diff(utime.ticks_ms(), self._prMillis) > BaseMQ.MQ_HEATING_PERIOD):
			return True
		else:
			return False

	def coolanceCompleted(self):
		if (self._heater) and (self._cooler) and (utime.ticks_diff(utime.ticks_ms(), self._prMillis) > BaseMQ.MQ_COOLING_PERIOD):
			return True
		else:
			return False

	def cycleHeat(self):
		self._heater = False
		self._cooler = False
		log("INFO", "Heating sensor...")
		self.heaterPwrHigh()
		pass

	def atHeatCycleEnd(self):
		if self.heatingCompleted():
			log("INFO", "Cooling sensor...")
			self.heaterPwrLow()
			return False

		elif self.coolanceCompleted():
			self.heaterPwrOff()
			return True

		else:
			return False
