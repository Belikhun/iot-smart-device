from features import FeatureAlarm

def register_features():
	FeatureAlarm(
		id="alarm",
		name="Alarm Buzzer",
		pin=27
	)
