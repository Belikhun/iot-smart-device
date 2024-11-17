#include "MQ2.h"
# Ported from https://github.com/amperka/TroykaMQ
# Author: Alexey Tveritinov [kartun@yandex.ru]
from .BaseMQ import BaseMQ
import math

class MQ2(BaseMQ):
	MQ2_RO_BASE = float(9.83)

	def __init__(self, pinData, pinHeater=-1, boardResistance = 10, baseVoltage = 5.0, measuringStrategy = BaseMQ.STRATEGY_ACCURATE):
		super().__init__(pinData, pinHeater, boardResistance, baseVoltage, measuringStrategy)
		pass

	async def readLPG(self):
		return await self.readScaled(-0.45, 2.95)

	async def readMethane(self):
		return await self.readScaled(-0.38, 3.21)

	async def readSmoke(self):
		return await self.readScaled(-0.42, 3.54)

	async def readHydrogen(self):
		return await self.readScaled(-0.48, 3.32)

	async def readAll(self):
		ratio = await self.readRatio()
		if (ratio <= 0):
			ratio = 0.01

		a = -0.45
		b = 2.95
		lpg = math.exp((math.log(ratio) - b) / a)

		a = -0.38
		b = 3.21
		methane = math.exp((math.log(ratio) - b) / a)

		a = -0.42
		b = 3.54
		smoke = math.exp((math.log(ratio) - b) / a)

		a = -0.48
		b = 3.32
		hydrogen = math.exp((math.log(ratio) - b) / a)

		return (lpg, methane, smoke, hydrogen)

	def getRoInCleanAir(self):
		return self.MQ2_RO_BASE
