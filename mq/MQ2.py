#include "MQ2.h"
# Ported from https://github.com/amperka/TroykaMQ
# Author: Alexey Tveritinov [kartun@yandex.ru]
from .BaseMQ import BaseMQ
from micropython import const

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

	def getRoInCleanAir(self):
		return self.MQ2_RO_BASE
