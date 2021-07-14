#!/usr/bin/env python3
from time import sleep
import paho.mqtt.client as mqtt
from gpiozero import PWMLED, Buzzer,LED


# Assigning hardware Macros
led = PWMLED(17)  # See Gpio zero for pin config
Emergency_light = LED(27) # See gpio zero
buzzer = Buzzer(22)
Fan = LED(26)

# MQTT part
MQTT_ADDRESS = '192.168.42.1'
MQTT_TOPIC = "Actuators"
MQTT_CLIENT_ID = 'ActuatorSend'



def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)
    
def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    global temperature,Gaslevel,Ldr,Piezo,hic,humidity,flame,co2
    print(msg.topic + ' ' + str(msg.payload))
    # sensor_data = _parse_mqtt_message(msg.topic, msg.payload.decode('utf-8'))
    payloadData = msg.payload.decode('utf-8')
    payloadDataValues = payloadData[1:len(payloadData) - 1].split(',')
    # for x in payloadDataValues:
    #     Actuator(x)
    Actuator(payloadDataValues)

def sendmail():
    print('Mail sent')

def Actuator(actuation_message):
    print('Message inside Function')
    print(actuation_message)
    if "'safe-state-no-emergency'" in actuation_message :
        buzzer.on()
        Emergency_light.on()
        led.on() 
        sleep(1)
        led.off()
        sleep(1)
    elif " 'temperature-control-off'" in actuation_message:
         Fan.off()
    elif actuation_message == 'send-mail':
          sendmail();  
    elif actuation_message == 'all-in-control':
          buzzer.off()
    elif actuation_message == 'notify-emergency':           
          buzzer.on()
          sendmail()
    elif actuation_message == 'temperature-control-on':
          Fan.on()    
    elif actuation_message == 'leicht-control-off':
          led.value = 0.3   # Low brightness
    elif actuation_message == 'leicht-control-on':
          led.value = 1.0   # Full brightness   
    

def main():
    #_init_influxdb_database()

    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()

if __name__ == '__main__':
    print('Actuator')
    main()    