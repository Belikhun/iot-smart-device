from features import FeatureButton, FeatureKnob

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
