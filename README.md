# SmartEd-Smart-Educational-Building
IoT project for the subject of Smart Cities and IoT

## Component files of the project
1. influxdb.py - publish senors values to the influx db
2. sensorsin.py - recieve sensors readings from Arduino and publish them to the topic "Sensors"
3. AdruinoInterface.cpp - Using Arduino to fetch data from Sensors and control Actuators
4. PDDL.py - updates the PDDL problem file with current sensor readings and gets the plan from the online pddl solver and publishes the plan to the topic ="actuators"
5. ActuatorGpiozero.py - Subscribes to the actuator topic and activates the individual actuators accordingly


