"""
APDS9960 Python + AWS example
Author: Nicolas Bauwens
Date: September 11th 2018
License: This code is public domain

Based on Sparkfuns Example code written by Thomas Liske

Read the proximity values from the SparkFun APDS9960 board

Tested on Raspberry Pi 3
"""
from apds9960.const import *
from apds9960 import APDS9960
import RPi.GPIO as GPIO
import smbus
from time import sleep
import os
import ConfigParser
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from datetime import datetime

class APDS9960:
    def __init__(self):
        self.port = 1
        self.bus = smbus.SMBus(self.port)
        self.apds = APDS9960(self.bus)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(7, GPIO.IN)

        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.dirname(os.path.abspath(__file__)) + '/../conf/app.cfg')
        self.config.sections()

    def intH(channel):
        print("INTERRUPT")

    def awsCallback(client, userdata, dummy, message):
        print(message.payload)

    def initAwsMqtt(self):
        # For certificate based connection
        global myMQTTClient
        myMQTTClient = AWSIoTMQTTClient(self.config.get('aws', 'client-name'),useWebsocket=False)
        print('IoT client name: ' + self.config.get('aws', 'client-name'))
        print('AWS endpoint: ' + self.config.get('aws', 'endpoint'))
        # Configurations
        # For TLS mutual authentication
        myMQTTClient.configureEndpoint(self.config.get('aws', 'endpoint'), self.config.get('aws', 'endpoint-port'))
        myMQTTClient.configureCredentials(self.config.get('aws', 'root-ca'), self.config.get('aws', 'private-key'), self.config.get('aws', 'certificate'))
        myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
        print('Trying to connect to AWS')
        myMQTTClient.connect()
        print('Connected to AWS')
        myMQTTClient.subscribe(self.config.get('aws', 'subscription-topic'), 1, self.awsCallback)
        print('Subscribed to topic : ' + self.config.get('aws', 'subscription-topic'))

def run():
        self.initAwsMqtt()
        try:
            # Interrupt-Event hinzufuegen, steigende Flanke
            GPIO.add_event_detect(7, GPIO.FALLING, callback = self.intH)

            self.apds.setProximityIntLowThreshold(50)

            print("Proximity Sensor Readings")
            print("=====================")
            self.apds.enableProximitySensor()
            oval = -1
            while True:
                sleep(0.25)
                val = self.apds.readProximity()
                if val != oval:
                    print("proximity={}".format(val))
                    currentDatetime = datetime.today().isoformat()
                    myMQTTClient.publish(self.config.get('aws', 'publish-topic'), '{"deviceId":"' + self.config.get('aws', 'device-id') + '", "date":"' + currentDatetime + '", "Proximity":' + '"' + str(val) + '"}', 0)
                    oval = val

        finally:
            GPIO.cleanup()
            myMQTTClient.disconnect()
            print "Bye"

a = APDS9960()
a.run()