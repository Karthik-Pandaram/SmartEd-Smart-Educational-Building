#include<Arduino.h>
#include "DHT.h"
//sensor intializations
#define DHTPIN 31     // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11 
DHT dht(DHTPIN, DHTTYPE);
#define MQ2 A1 // MQ2 gas sensor analog pin number
#define LDR A3 // LDR module analog pin number
#define Peizo A7 //Piezo module analog pin number
int gaslevel = 0;
int Ldr_value = 0;
int Piezo= 0 ;
int buffer = 0;
float humidity = 0;
float temperature = 0;
// Intializing Raspberry Pi serial communication
//Raspberry Pi is connected to Serial 0
#define serialPi Serial
// define sensor 
# define buzz 11 // set a digital pin as buzzer
void setup()
{
  //Serial.begin(9600); //Initialize serial port - 9600 bps
  serialPi.begin(9600); //Arduino to serial monitor
  pinMode(MQ2,INPUT);   // Set the analog pin as input for MQ2
  pinMode(LDR, INPUT); // Set the analog pin as input for LDR
  pinMode(buzz, OUTPUT); // Set the BUZZ pin as output to activate buzzer
  dht.begin();
}
void loop()
{
  gaslevel=(analogRead(MQ2));
  gaslevel=map(gaslevel,0,250,0,255);
  //Serial.print("Gas = ");
  //Serial.print(gaslevel);
  //Serial.print("\n");
  delay(1000);
  Ldr_value = (analogRead(LDR));
  Ldr_value = map(Ldr_value,0,1023,0,255); // Low value indicates light and high value indicates Darkness
  //Serial.print("LDR = ");
  //Serial.print(Ldr_value);
  //Serial.print("\n");
  delay(500);
  Piezo = (analogRead(Peizo));
  //Serial.print("Peizo sensor = \t");
  //Serial.print(Peizo);
  //Serial.print("\n");
  delay(2000);
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float humidity = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float temperature = dht.readTemperature();
  delay(500);
  // Compute heat index in Celsius (isFahreheit = false)
  float hic = dht.computeHeatIndex(temperature, humidity, false);
  /*Serial.print(F(" Humidity: "));
  Serial.print(h);
  Serial.print(F("%  Temperature: "));
  Serial.print(t);
  Serial.print(F("C "));
  Serial.print(F(" Heat index: "));
  Serial.print(hic);
  Serial.print(F("C "));
  */
 //Send temperature and humidity data to Raspberry Pi
  serialPi.print("<");
  serialPi.print(temperature);
  serialPi.print(",");
  serialPi.print(gaslevel);
  serialPi.print(",");
  serialPi.print(Ldr_value);
  serialPi.print(",");
  serialPi.print(Piezo);
  serialPi.print(",");
  serialPi.print(hic);
  serialPi.print(",");
  serialPi.print(humidity);
  serialPi.println(">");
  delay(1000);
  // Actuation aprt
  if (serialPi.available() > 0) {
    String data = serialPi.readStringUntil('\n');
    serialPi.println(data);
    buffer = data.toInt();
  }
  if (buffer == 10)
  {
    digitalWrite(buzz, HIGH);
    delay(1000);
    digitalWrite(buzz,LOW);
  }
  buffer = 0 ;
}
