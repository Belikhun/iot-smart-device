from features import FeatureButton, FeatureKnob, FeatureTemperature, FeatureHumidity
import uasyncio as asyncio
import machine
import dht
from logger import log

def register_features():
	FeatureKnob(
		id="rotary1",
		name="Rotary Knob",
		pin_clk=34,
		pin_dt=35
	)

	FeatureButton(
		id="rotary1/button",
		name="Rotary Button",
		pin=32,
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
				temperature.set_value(current_temp)

			if (abs(humidity.get_value() - current_humid) > 0.01):
				humidity.set_value(current_humid)

			await asyncio.sleep(1)
	
	asyncio.create_task(update_dht())
