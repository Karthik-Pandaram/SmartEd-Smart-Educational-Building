import datetime
import paho.mqtt.client as mqtt
import pytz
import json
import logging
import time
import pickle
import urllib, sys
import re
import requests
import paho.mqtt.publish as publish
#from influxdb import InfluxDBClient

# INFLUXDB_ADDRESS = '10.0.2.15'
# INFLUXDB_USER = 'dietpi'
# INFLUXDB_PASSWORD = 'dietpi'
# INFLUXDB_DATABASE = 'smart_monitoring'
MQTT_ADDRESS = '192.168.42.1'
MQTT_TOPIC = 'Sensors'
MQTT_CLIENT_ID = 'PDDL'
MQTT_PATH = "Actuators"
#influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)

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
    temperature = payloadDataValues[0]
    Gaslevel = payloadDataValues[1]
    Ldr = payloadDataValues[2]
    Piezo = payloadDataValues[3]
    hic = payloadDataValues[4]
    humidity = payloadDataValues[5]
    flame = payloadDataValues[6]
    co2 = payloadDataValues[7]
    update_problem_pddl()
    plan = get_pddl_plan()
    print (plan)
    publish_action()

def update_problem_pddl():
    problem_pddl_str=""
    with open("Monitor_problem.pddl") as fin:
        problem_pddl_str = fin.read()
    temperature_str = "(= (temperature f) " + str(temperature) +")"
    humidity_str = "(= (humidity f) " + str(humidity) +")"
    luminance_str = "(= (lux f) " + str(Ldr) +")"
    co2_str = "(= (co2 f) " + str(co2) +")" 
    piezo_str = "(= (piezo f) " + str(Piezo) +")" 
    flame_str = "(= (flame f) " + str(flame) +")" 
    problem_pddl_str =  re.sub('\(= \(temperature f\) [0-9.]+\)', temperature_str, problem_pddl_str)
    problem_pddl_str =  re.sub('\(= \(humidity f\) [0-9.]+\)', humidity_str, problem_pddl_str)
    problem_pddl_str =  re.sub('\(= \(lux f\) [0-9.]+\)', luminance_str, problem_pddl_str)
    problem_pddl_str =  re.sub('\(= \(co2 f\) [0-9.]+\)', co2_str, problem_pddl_str)
    problem_pddl_str =  re.sub('\(= \(piezo f\) [0-9.]+\)', piezo_str, problem_pddl_str)
    problem_pddl_str =  re.sub('\(= \(flame f\) [0-9.]+\)', flame_str, problem_pddl_str)
    with open("Monitor_problem.pddl", "w") as fout:
        fout.write(problem_pddl_str)

def get_pddl_plan():
    # Get plan from online planner
    # Publish to mqtt
    data = {'domain': open("smarted_domain.pddl", 'r').read(),
        'problem': open("Monitor_problem.pddl", 'r').read()}

    # req = Request('http://solver.planning.domains/solve')
    # req.add_header('Content-Type', 'application/json')
    # resp = json.loads(urlopen(req, json.dumps(data)).read())
    response = requests.post('http://solver.planning.domains/solve', json=data).json()
    actresult = []
    for act in response['result']['plan']:
        step = act['name']
        actuations = step[1:len(step)-1].split(' ')
        actresult.append(actuations)
    return actresult            

def publish_action():
    action = get_pddl_plan()
    action_publish = []
    for x in range(0,len(action)):
       action_publish.append(action[x][0])
    
    payload = str(action_publish)
    publish.single(MQTT_PATH, payload, hostname=MQTT_ADDRESS)            
# def _init_influxdb_database():
#     databases = influxdb_client.get_list_database()
#     if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
#         influxdb_client.create_database(INFLUXDB_DATABASE)
#     influxdb_client.switch_database(INFLUXDB_DATABASE)
    
def main():
    #_init_influxdb_database()

    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()
    
if __name__ == '__main__':
    print('PDDL update problem with current sensor values and get plan')
    
    main()
