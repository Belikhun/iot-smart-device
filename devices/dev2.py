from features import FeatureButton, FeatureKnob, FeatureTemperature, FeatureHumidity, FeatureSensorValue
from features.utils import FeatureUpdateSource
import uasyncio as asyncio
import machine
import dht
from mq import MQ2
from logger import log, scope

def register_features():
	FeatureKnob(
		id="rotary1",
		name="Rotary Knob",
		pin_clk=33,
		pin_dt=25
	)

	FeatureButton(
		id="rotary1/button",
		name="Rotary Button",
		pin=26,
		default=False
	)

	temperature = FeatureTemperature(
		id="temp",
		name="Temperature"
	)

	humidity = FeatureHumidity(
		id="humid",
		name="Humidity"
	)

	async def update_dht():
		sensor = dht.DHT11(machine.Pin(4))
		await asyncio.sleep(2)

		while True:
			try:
				sensor.measure()
			except Exception as e:
				log("WARN", f"Read values from DHT sensor failed: {e}")
				await asyncio.sleep(1)
				continue

			current_temp = sensor.temperature()
			current_humid = sensor.humidity()

			if (abs(temperature.get_value() - current_temp) > 0.01):
				temperature.set_value(current_temp, update_source=FeatureUpdateSource.HARDWARE)

			if (abs(humidity.get_value() - current_humid) > 0.01):
				humidity.set_value(current_humid, update_source=FeatureUpdateSource.HARDWARE)

			await asyncio.sleep(1)
	
	asyncio.create_task(update_dht())

	smoke = FeatureSensorValue(
		id="smoke",
		name="Smoke Concentration",
		max=200,
		dangerous=100,
		unit="ppm"
	)

	lpg = FeatureSensorValue(
		id="lpg",
		name="LPG Concentration",
		max=3000,
		dangerous=2000,
		unit="ppm"
	)

	methane = FeatureSensorValue(
		id="methane",
		name="Methane Concentration",
		max=6000,
		dangerous=5000,
		unit="ppm"
	)

	hydrogen = FeatureSensorValue(
		id="hydrogen",
		name="Hydrogen Concentration",
		max=5000,
		dangerous=4000,
		unit="ppm"
	)

	async def update_mq2():
		log = scope("mq2")

		sensor = MQ2(pinData=35, baseVoltage=5, measuringStrategy=MQ2.STRATEGY_FAST)
		await sensor.calibrate()

		log("INFO", f"Calibration completed. Base resistance: {sensor._ro}")

		while True:
			try:
				smoke_value = await sensor.readSmoke()
				log("DEBG", f"Smoke: {smoke_value} ppm")
				smoke.set_value(smoke_value)

				lpg_value = await sensor.readLPG()
				log("DEBG", f"LPG: {lpg_value} ppm")
				lpg.set_value(lpg_value)

				methane_value = await sensor.readMethane()
				log("DEBG", f"Methane: {methane_value} ppm")
				methane.set_value(methane_value)

				hydrogen_value = await sensor.readHydrogen()
				log("DEBG", f"Hydrogen: {hydrogen_value} ppm")
				hydrogen.set_value(hydrogen_value)
				await asyncio.sleep(2)
			except Exception as e:
				log("WARN", f"Read values from MQ-2 sensor failed: {e}")
				await asyncio.sleep(2)
				continue

	asyncio.create_task(update_mq2())
