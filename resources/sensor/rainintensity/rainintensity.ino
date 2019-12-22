//moisture_Sensor pins
#define moisture_SensorPin01 A0
#define moisture_SensorPin02 A1
#define moisture_SensorPin03 A2
#define moisture_SensorPin04 A3

//variables for the each sensor, mapping and averaging
int moistureSensor01 = 0, moistureSensor02 = 0, moistureSensor03 = 0, moistureSensor04 = 0;
int map_moistureSensor01 = 0, map_moistureSensor02 = 0, map_moistureSensor03 = 0, map_moistureSensor04 = 0;
int total_moistureSensorAverage = 0;

//setup pins as input on arduino boot
void setup() { 
  pinMode(moisture_SensorPin01, INPUT);
  pinMode(moisture_SensorPin02, INPUT);
  pinMode(moisture_SensorPin03, INPUT);
  pinMode(moisture_SensorPin04, INPUT);

  Serial.begin(9600);
} 

void loop() {
  //do nothing until crosstalk with python has not been initiated
  while (!Serial.available()) {}

  //proceed with recording, averaging and output data to serial
  while (Serial.available()) {
    for (int i = 0; i <= 100; i++) { 
      moistureSensor01 = moistureSensor01 + analogRead(moisture_SensorPin01);
      moistureSensor02 = moistureSensor02 + analogRead(moisture_SensorPin02); 
      moistureSensor03 = moistureSensor03 + analogRead(moisture_SensorPin03); 
      moistureSensor04 = moistureSensor04 + analogRead(moisture_SensorPin04); 

      delay(1); 
    }

    moistureSensor01 = moistureSensor01 / 100; 
    moistureSensor02 = moistureSensor02 / 100; 
    moistureSensor03 = moistureSensor03 / 100; 
    moistureSensor04 = moistureSensor04 / 100;

    map_moistureSensor01 = map(moistureSensor01,1023,10,0,100);
    map_moistureSensor02 = map(moistureSensor02,1023,10,0,100);
    map_moistureSensor03 = map(moistureSensor03,1023,10,0,100);
    map_moistureSensor04 = map(moistureSensor04,1023,10,0,100);

    total_moistureSensorAverage = map_moistureSensor01 + map_moistureSensor02 + map_moistureSensor03 + map_moistureSensor04;

    Serial.println("01.  " + String(map_moistureSensor01) + " | 02.  " + String(map_moistureSensor02) + " | 03.  " + String(map_moistureSensor03) + " | 04.  " + String(map_moistureSensor04)+ " | Average:  " + String(total_moistureSensorAverage));    
    Serial.println(total_moistureSensorAverage);
    delay(1000); 
  }
}
