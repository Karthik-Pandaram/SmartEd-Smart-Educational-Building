import datetime
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
INFLUXDB_ADDRESS = '192.168.42.1'
INFLUXDB_USER = 'dietpi'
INFLUXDB_PASSWORD = 'dietpi'
INFLUXDB_DATABASE = 'smart_monitoring'
MQTT_ADDRESS = '192.168.42.1'
MQTT_TOPIC = 'Sensors'
MQTT_CLIENT_ID = 'MQTTInfluxDBBridge'
influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, None)
def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)
def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))
    # sensor_data = _parse_mqtt_message(msg.topic, msg.payload.decode('utf-8'))
    payloadData = msg.payload.decode('utf-8')
    payloadDataValues = payloadData[1:len(payloadData) - 1].split(',')
    temperature = payloadDataValues[0]
    Gaslevel = payloadDataValues[1]
    LDR = payloadDataValues[2]
    Piezo = payloadDataValues[3]
    hic = payloadDataValues[4]
    humidity = payloadDataValues[5]
    if (temperature and Gaslevel) is not None:
        json_body = [
            {
                'measurement': 'Sensors_values',
                'time': str(datetime.datetime.now()),
                'fields': {
                    'temperature': temperature,
                    'Gas_level': Gaslevel,
                    'LDR': LDR,
                    'Piezo': Piezo,
                    'hic': hic,
                    'humidity': humidity
                }
            }
        ]
        influxdb_client.write_points(json_body)
    else:
        print("Empty values")
def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)
def main():
    _init_influxdb_database()
    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()
if __name__ == '__main__':
    print('MQTT to InfluxDB bridge')
    main()
    
