from features import FeatureButton, FeatureKnob

def register_features():
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

	FeatureButton(
		id="rotary_button",
		name="Rotary Button",
		pin=35
	)

	FeatureKnob(
		id="rotary",
		name="Rotary Encoder",
		pin_clk=33,
		pin_dt=32
	)
