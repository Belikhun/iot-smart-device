from features import FeatureAlarm, FeatureOnOffSensor

def register_features():
	FeatureAlarm(
		id="alarm",
		name="Alarm Buzzer",
		pin=27
	)

	FeatureOnOffSensor(
		id="lightSensor",
		name="Light Sensor",
		pin=18,
		flip=True
	)
