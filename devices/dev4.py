from features import FeatureFanMotor

def register_features():
	FeatureFanMotor(
		id="fan",
		name="Fan",
		pin_a=18,
		pin_b=19
	)
