#include<Arduino.h>
#include "DHT.h"
/******************Hardware Macros / Sensor pin assignments*********************/

#define DHTPIN 31     // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11 
DHT dht(DHTPIN, DHTTYPE);
//#define MQ_PIN A1     // MQ2 gas sensor analog pin number
#define LDR A3        // LDR module analog pin number
#define Peizo A7      //Piezo module analog pin number
#define Flame A10     // IR Flame sensor 
int gaslevel = 0;
int Ldr_value = 0;
int Piezo= 0 ;
int buffer = 0;
float humidity = 0;
float temperature = 0;
int Flame_sensor = 0;
// Intializing Raspberry Pi serial communication
//Raspberry Pi is connected to Serial 0
#define serialPi Serial
// define sensor 
# define buzz 11 // set a digital pin as buzzer

/****Calibrating the MQ2 sensor****************/
const int calibrationLed = 13;                      //when the calibration start , LED pin 13 will light up , off when finish calibrating
const int MQ_PIN= A1;                                //define which analog input channel you are going to use
int RL_VALUE=5;                                     //define the load resistance on the board, in kilo ohms
float RO_CLEAN_AIR_FACTOR=9.83;                     //RO_CLEAR_AIR_FACTOR=(Sensor resistance in clean air)/RO,
// const int calibrationLed = 13;                      //when the calibration start , LED pin 13 will light up , off when finish calibrating
// //const int MQ_PIN=A0;                                //define which analog input channel you are going to use
// int RL_VALUE=5;                                     //define the load resistance on the board, in kilo ohms
// float RO_CLEAN_AIR_FACTOR=9.83;                     //RO_CLEAR_AIR_FACTOR=(Sensor resistance in clean air)/RO,
                                                    //which is derived from the chart in datasheet

/***********************Software Related Macros************************************/
int CALIBARAION_SAMPLE_TIMES=50;                    //define how many samples you are going to take in the calibration phase
int CALIBRATION_SAMPLE_INTERVAL=500;                //define the time interal(in milisecond) between each samples in the
                                                    //cablibration phase
int READ_SAMPLE_INTERVAL=50;                        //define how many samples you are going to take in normal operation
int READ_SAMPLE_TIMES=5;                            //define the time interal(in milisecond) between each samples in 
                                                    //normal operation
// int CALIBARAION_SAMPLE_TIMES=50;                    //define how many samples you are going to take in the calibration phase
// int CALIBRATION_SAMPLE_INTERVAL=500;                //define the time interal(in milisecond) between each samples in the
//                                                     //cablibration phase
// int READ_SAMPLE_INTERVAL=50;                        //define how many samples you are going to take in normal operation
// int READ_SAMPLE_TIMES=5;                            //define the time interal(in milisecond) between each samples in 
 
/**********************Application Related Macros**********************************/
#define         GAS_LPG             0   
#define         GAS_CO              1   
#define         GAS_SMOKE           2    
 
/*****************************Globals***********************************************/
float           LPGCurve[3]  =  {2.3,0.21,-0.47};   //two points are taken from the curve. 
                                                    //with these two points, a line is formed which is "approximately equivalent"
                                                    //to the original curve. 
                                                    //data format:{ x, y, slope}; point1: (lg200, 0.21), point2: (lg10000, -0.59) 
float           COCurve[3]  =  {2.3,0.72,-0.34};    //two points are taken from the curve. 
                                                    //with these two points, a line is formed which is "approximately equivalent" 
                                                    //to the original curve.
                                                    //data format:{ x, y, slope}; point1: (lg200, 0.72), point2: (lg10000,  0.15) 
float           SmokeCurve[3] ={2.3,0.53,-0.44};    //two points are taken from the curve. 
                                                    //with these two points, a line is formed which is "approximately equivalent" 
                                                    //to the original curve.
                                                    //data format:{ x, y, slope}; point1: (lg200, 0.53), point2: (lg10000,  -0.22)                                                     
float           Ro           =  10;                 //Ro is initialized to 10 kilo ohms

/************* Light intensity measurement**********************************/
int lux = 0;

/*******************Function for calibration**********************************/

/****************** MQResistanceCalculation ****************************************
Input:   raw_adc - raw value read from adc, which represents the voltage
Output:  the calculated sensor resistance
Remarks: The sensor and the load resistor forms a voltage divider. Given the voltage
         across the load resistor and its resistance, the resistance of the sensor
         could be derived.
************************************************************************************/ 
float MQResistanceCalculation(int raw_adc)
{
  return ( ((float)RL_VALUE*(1023-raw_adc)/raw_adc));
}
 
/***************************** MQCalibration ****************************************
Input:   mq_pin - analog channel
Output:  Ro of the sensor
Remarks: This function assumes that the sensor is in clean air. It use  
         MQResistanceCalculation to calculates the sensor resistance in clean air 
         and then divides it with RO_CLEAN_AIR_FACTOR. RO_CLEAN_AIR_FACTOR is about 
         10, which differs slightly between different sensors.
************************************************************************************/ 
float MQCalibration(int mq_pin)
{
  int i;
  float val=0;

  for (i=0;i<CALIBARAION_SAMPLE_TIMES;i++) {            //take multiple samples
    val += MQResistanceCalculation(analogRead(mq_pin));
    delay(CALIBRATION_SAMPLE_INTERVAL);
  }
  val = val/CALIBARAION_SAMPLE_TIMES;                   //calculate the average value
  val = val/RO_CLEAN_AIR_FACTOR;                        //divided by RO_CLEAN_AIR_FACTOR yields the Ro                                        
  return val;                                                      //according to the chart in the datasheet 

}
 
/*****************************  MQRead *********************************************
Input:   mq_pin - analog channel
Output:  Rs of the sensor
Remarks: This function use MQResistanceCalculation to caculate the sensor resistenc (Rs).
         The Rs changes as the sensor is in the different consentration of the target
         gas. The sample times and the time interval between samples could be configured
         by changing the definition of the macros.
************************************************************************************/ 
float MQRead(int mq_pin)
{
  int i;
  float rs=0;
 
  for (i=0;i<READ_SAMPLE_TIMES;i++) {
    rs += MQResistanceCalculation(analogRead(mq_pin));
    delay(READ_SAMPLE_INTERVAL);
  }
 
  rs = rs/READ_SAMPLE_TIMES;
 
  return rs;  
}

/*****************************  MQGetPercentage **********************************
Input:   rs_ro_ratio - Rs divided by Ro
         pcurve      - pointer to the curve of the target gas
Output:  ppm of the target gas
Remarks: By using the slope and a point of the line. The x(logarithmic value of ppm) 
         of the line could be derived if y(rs_ro_ratio) is provided. As it is a 
         logarithmic coordinate, power of 10 is used to convert the result to non-logarithmic 
         value.
************************************************************************************/ 
long  MQGetPercentage(float rs_ro_ratio, float *pcurve)
{
  return (pow(10,( ((log(rs_ro_ratio)-pcurve[1])/pcurve[2]) + pcurve[0])));
}

/*****************************  MQGetGasPercentage **********************************
Input:   rs_ro_ratio - Rs divided by Ro
         gas_id      - target gas type
Output:  ppm of the target gas
Remarks: This function passes different curves to the MQGetPercentage function which 
         calculates the ppm (parts per million) of the target gas.
************************************************************************************/ 
long MQGetGasPercentage(float rs_ro_ratio, int gas_id)
{
  
  if ( gas_id == GAS_LPG ) {
     return MQGetPercentage(rs_ro_ratio,LPGCurve);
  } else if ( gas_id == GAS_CO ) {
     return MQGetPercentage(rs_ro_ratio,COCurve);
  } else if ( gas_id == GAS_SMOKE ) {
     return MQGetPercentage(rs_ro_ratio,SmokeCurve);
  }    
 
  return 0;
}
 












void setup()
{
  //Serial.begin(9600); //Initialize serial port - 9600 bps
  serialPi.begin(9600); //Arduino to serial monitor
  //pinMode(MQ2,INPUT);   // Set the analog pin as input for MQ2
  pinMode(LDR, INPUT); // Set the analog pin as input for LDR
  pinMode(buzz, OUTPUT); // Set the BUZZ pin as output to activate buzzer
  dht.begin();
  /******************MQ2 ************/
  Ro = MQCalibration(MQ_PIN);
}
void loop()
{
  /******Calibrated MQ2***************/
  long iPPM_LPG = 0;
  long iPPM_CO = 0;
  long iPPM_Smoke = 0;

  iPPM_LPG = MQGetGasPercentage(MQRead(MQ_PIN)/Ro,GAS_LPG);
  iPPM_CO = MQGetGasPercentage(MQRead(MQ_PIN)/Ro,GAS_CO);
  iPPM_Smoke = MQGetGasPercentage(MQRead(MQ_PIN)/Ro,GAS_SMOKE);
  
  //gaslevel=(analogRead(MQ2));
  //gaslevel=map(gaslevel,0,250,0,255);

  //Serial.print("Gas = ");
  //Serial.print(gaslevel);
  //Serial.print("\n");
  delay(1000);
  Ldr_value = (analogRead(LDR));
  Ldr_value =analogRead(LDR) * (5.0 / 1023.0);  // (5 / 1023 ) is the conversion factor to get value in Volts.
  lux = (250 / Ldr_value) - 50;

  //Ldr_value = map(Ldr_value,0,1023,0,255); // Low value indicates light and high value indicates Darkness
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
 /*****************Flame sensor part*****************************/
  Flame_sensor = analogRead(Flame);

  

  //activate the buzzer

  // if (valorSensor < 500){

  // digitalWrite(buzzer, HIGH);

  delay(100);
              //Send temperature and humidity data to Raspberry Pi
  gaslevel = 10;
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
  serialPi.print(",");
  serialPi.print(Flame_sensor);
  serialPi.print(",");
  serialPi.print(iPPM_CO);
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

/*********************************************Reference codes*************************************************/


/****** remove after code runs ****/
/*
void setup()
{ 
  
  lcd.begin(20,4);
  pinMode(calibrationLed,OUTPUT);
  digitalWrite(calibrationLed,HIGH);
  lcd.print("Calibrating...");                        //LCD display

  
  Ro = MQCalibration(MQ_PIN);                         //Calibrating the sensor. Please make sure the sensor is in clean air         
  digitalWrite(calibrationLed,LOW);              
  
  lcd.print("done!");                                 //LCD display
  lcd.setCursor(0,1);
  lcd.print("Ro= ");
  lcd.print(Ro);
  lcd.print("kohm");
  delay(3000);
}
 
void loop()
{  
  long iPPM_LPG = 0;
  long iPPM_CO = 0;
  long iPPM_Smoke = 0;

  iPPM_LPG = MQGetGasPercentage(MQRead(MQ_PIN)/Ro,GAS_LPG);
  iPPM_CO = MQGetGasPercentage(MQRead(MQ_PIN)/Ro,GAS_CO);
  iPPM_Smoke = MQGetGasPercentage(MQRead(MQ_PIN)/Ro,GAS_SMOKE);
  
   lcd.clear();   
   lcd.setCursor( 0 , 0 );
   lcd.print("Concentration of gas ");
   
   lcd.setCursor( 0 , 1 );
   lcd.print("LPG: ");
   lcd.print(iPPM_LPG);
   lcd.print(" ppm");   
   
   lcd.setCursor( 0, 2 );
   lcd.print("CO: ");
   lcd.print(iPPM_CO);
   lcd.print(" ppm");    

   lcd.setCursor( 0,3 );
   lcd.print("Smoke: ");
   lcd.print(iPPM_Smoke);
   lcd.print(" ppm");  

   delay(200);
  
}
*/




 


