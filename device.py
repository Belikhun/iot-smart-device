from features import FeatureRGBLed, FeatureOnOffPin, FeatureButton

def init_features():
	FeatureRGBLed(
		id="rgb1",
		name="RGB Led",
		red_pin=14,
		green_pin=32,
		blue_pin=33
	)

	FeatureOnOffPin(
		id="relay1",
		name="Relay 1",
		pin=22,
		flip=True
	)

	FeatureOnOffPin(
		id="relay2",
		name="Relay 2",
		pin=23,
		flip=True
	)

	FeatureButton(
		id="button1",
		name="Button 1",
		pin=25
	)

	FeatureButton(
		id="button2",
		name="Button 2",
		pin=26
	)

	FeatureButton(
		id="button3",
		name="Button 3",
		pin=27
	)

	pass
