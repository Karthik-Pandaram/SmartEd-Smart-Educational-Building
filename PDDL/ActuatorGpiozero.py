#!/usr/bin/env python3
from time import sleep
import paho.mqtt.client as mqtt
from gpiozero import PWMLED, Buzzer,LED
import RPi.GPIO as GPIO
import smtplib, ssl



# Assigning hardware Macros
led = LED(17)  # See Gpio zero for pin config
Emergency_light = LED(27) # See gpio zero
buzzer = Buzzer(22)
Fan = LED(26)
# PWM led config
led_pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

#frequency 500 Hz
led_pwm = GPIO.PWM(led_pin, 500)
#duty cycle = 100
led_pwm.start(100)

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

def sendmailFirerescue():
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "writer.banu11@gmail.com"  # Enter your address
    receiver_email = "karthikp0712@gmail.com"  # Enter receiver address
    password = "Dreambig@1"
    message = """\
Subject: Fire Emergency 

There is a Fire emergency at the School """
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    	server.login(sender_email, password)
    	server.sendmail(sender_email, receiver_email, message)

def sendmail_Parent():
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "writer.banu11@gmail.com"  # Enter your address
    receiver_email = "karthikp0712@gmail.com"  # Enter receiver address
    password = "Dreambig@1"
    message = """\
Subject: Emergency at School 

There is a emergency at the School please report at the school parking to pickup your children """
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    	server.login(sender_email, password)
    	server.sendmail(sender_email, receiver_email, message)

def sendmail_Structure_Rescue():
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "writer.banu11@gmail.com"  # Enter your address
    receiver_email = "karthikp0712@gmail.com"  # Enter receiver address
    password = "Dreambig@1"
    message = """\
Subject: Structural Hazard  

The Stuructural intergrity of the School is poor, it may collapse """
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    	server.login(sender_email, password)
    	server.sendmail(sender_email, receiver_email, message)

def Actuator(actuation_message):
    print('Message inside Function')
    print(actuation_message)

    if ("'Fire-send-mail'") in actuation_message:
        sendmailFirerescue()
        sendmail_Parent()
        print('1')
    
    if (" 'Fire-send-mail'") in actuation_message:
        sendmailFirerescue()
        sendmail_Parent()
        print('1')

    if ("'Structure-send-mail'")  in actuation_message:
        sendmail_Parent()
        sendmail_Structure_Rescue()
        print('2')
    if (" 'Structure-send-mail'") in actuation_message:
        sendmail_Parent()
        sendmail_Structure_Rescue()
        print('2')

    if ("'in-control'")  in actuation_message:
         buzzer.off() 
         print('3')

    if (" 'in-control'") in actuation_message:
         buzzer.off()
         print(3)

    if ("'notify-emergency'") in actuation_message:
         print('4')
         buzzer.on()
         sleep(1)
         buzzer.off()
         sleep(1)
    if  (" 'notify-emergency'") in actuation_message:
         print('4')
         buzzer.on()
         sleep(1)
         buzzer.off()
         sleep(1)
    if ("'turn-off-temperature-control'") in actuation_message:
          print('6')
          Fan.off()
          sleep(1)
    if (" 'turn-off-temperature-control'") in actuation_message:
          print('6')
          Fan.off()
          sleep(1)          
    if ("'turn-on-temperature-control'") in actuation_message:
          print('7')
          Fan.on()
          sleep(1)
    if (" 'turn-on-temperature-control'") in actuation_message: 
          print('7')
          Fan.on()
          sleep(1)  
    if "'leicht-control-off'" in actuation_message:
         print('8')
         led_pwm.ChangeDutyCycle(10)
         sleep(1)  # Low brightness
    if "'leicht-control-on'" in actuation_message:
         print('9')
         led_pwm.ChangeDutyCycle(100) 
         sleep(1)   # Full brightness   
  

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

 
