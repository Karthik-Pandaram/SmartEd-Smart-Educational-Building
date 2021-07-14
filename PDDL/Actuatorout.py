#!/usr/bin/env python3
import serial
import time
import paho.mqtt.client as mqtt

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
    for x in payloadDataValues:
        Actuator_serial(x)
    

def Actuator_serial(actuation_message):
       # ser.write(b"10\n")
    if (ser.in_waiting > 0):
      ser.write(b"10\n")
      ser.write(b(str(actuation_message)))
      b = ser.read(1)
      num = int.from_bytes(b, byteorder='big')
    


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