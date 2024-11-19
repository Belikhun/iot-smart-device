from features import FeatureButton, FeatureKnob, FeatureTemperature, FeatureHumidity, FeatureSensorValue
from features.utils import FeatureUpdateSource
import uasyncio as asyncio
import machine
import dht
from mq import MQ2
from logger import log, scope

def register_features():
	pass
