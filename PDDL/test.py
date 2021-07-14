import datetime
import paho.mqtt.client as mqtt
import pytz
import json
import logging
import time
import pickle
import urllib3, sys
import re
from urllib.request import Request, urlopen
import requests
def sensors():
    global temperature,Gaslevel,Ldr,Piezo,hic,humidity,flame,co2 
    temperature,Ldr,Piezo,humidity,flame,co2 = 1,2,3,4,5,6


def update_problem_pddl():
    problem_pddl_str=""
    with open("my.pddl") as fin:
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
    with open("my.pddl", "w") as fout:
        fout.write(problem_pddl_str)
    
def get_pddl_plan():
    # Get plan from online planner
    # Publish to mqtt
    data = {'domain': open("smarted_domain.pddl", 'r').read(),
        'problem': open("my.pddl", 'r').read()}

    # req = Request('http://solver.planning.domains/solve')
    # req.add_header('Content-Type', 'application/json')
    # resp = json.loads(urlopen(req, json.dumps(data)).read())
    response = requests.post('http://solver.planning.domains/solve', json=data).json()
    actresult = []
    for act in response['result']['plan']:
        step = act['name']
        actuations = step[1:len(step)-1].split(' ')
        actresult.append(actuations)
    return print(actresult)
    #return ('\n'.join([act['name'] for act in resp['result']['plan']]))

if __name__ == '__main__':
   
    sensors()
    update_problem_pddl()
    get_pddl_plan()
