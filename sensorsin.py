# rpi-arduino-dht11
# Raspberry Pi reads temperature and humidity sensor data from Arduino

import serial, string, time
from serial import Serial
import paho.mqtt.publish as publish

# In this example /dev/ttyUSB0 is used
# This may change in your case to /dev/ttyUSB1, /dev/ttyUSB2, etc.
ser = serial.Serial('/dev/ttyACM0', 9600)
# MQTT declaration part
MQTT_SERVER = "localhost"
MQTT_PATH = "Sensors"
# The following block of code works like this:
# If serial data is present, read the line, decode the UTF8 data,
# ...remove the trailing end of line characters
# ...split the data into temperature and humidity
# ...remove the starting and ending pointers (< >)
# ...print the output
while True:
        if ser.in_waiting > 0:
            rawserial = ser.readline()
            cookedserial = rawserial.decode('utf-8').strip('\r\n')
            datasplit = cookedserial.split(',')
            temperature = datasplit[0].strip('<')
            temperature = int(float(temperature))
            Gaslevel = int(datasplit[1])
            Ldr = int(datasplit[2])
            Piezo = int(datasplit[3])
            hic = int(datasplit[4])
            humidity =  datasplit[5].strip('>')
            humidity = int(float(humidity))
            flame = int(datasplit[6])
            co2 = int(datasplit[7].strip('>'))
            print(temperature)
            print(Gaslevel)
            print(Ldr)
            print(Piezo)
            print(hic)
            print(humidity)
            print(flame)
            print(co2)
            data = [temperature, Gaslevel, Ldr, Piezo, hic, humidity, flame, co2]
            payload = str(data)
            publish.single(MQTT_PATH, payload, hostname=MQTT_SERVER)
            time.sleep(1)
