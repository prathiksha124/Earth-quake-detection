#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include <ESP8266WiFi.h>
#include <FirebaseESP8266.h>
#include <math.h>


const char* ssid ="Prathiksha";
const char* password ="0987654321";


#define FIREBASE_HOST "removed due to risk"
#define FIREBASE_AUTH ""


FirebaseData fbdo;
FirebaseConfig config;
FirebaseAuth auth;

Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);


#define BUZZER_PIN D5


#define EARTHQUAKE_THRESHOLD 10.1

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); 
    Serial.print(".");
  }
  Serial.println("\n✅ Connected to WiFi");

  // Initialize Firebase
  config.host = FIREBASE_HOST;
  config.signer.tokens.legacy_token = FIREBASE_AUTH;
  
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  // Initialize ADXL345 accelerometer
  if (!accel.begin(0x1D)) {
    if (!accel.begin(0x53)) {
      Serial.println("❌ ADXL345 not detected!");
      while (1) delay(1000);
    } else {
      Serial.println("✅ ADXL345 detected at 0x53");
    }
  } else {
    Serial.println("✅ ADXL345 detected at 0x1D");
  }

  accel.setRange(ADXL345_RANGE_16_G);
}

void loop() {
  sensors_event_t event;
  accel.getEvent(&event);

  float x = event.acceleration.x;
  float y = event.acceleration.y;
  float z = event.acceleration.z;

  float magnitude = sqrt(x * x + y * y + z * z);
  
  if (magnitude > 10.2) {
    digitalWrite(BUZZER_PIN, HIGH);  
  } else {
    digitalWrite(BUZZER_PIN, LOW);   
  }
  Serial.print("X: "); Serial.print(x);
  Serial.print(" Y: "); Serial.print(y);
  Serial.print(" Z: "); Serial.print(z);
  Serial.print(" | Magnitude: "); Serial.println(magnitude);

  bool isEarthquake = magnitude >= EARTHQUAKE_THRESHOLD;

  if(isEarthquake){
    Serial.println("⚠️ EARTHQUAKE ALERT!");

      Firebase.setBool(fbdo, "/ml_trigger", true);
    delay(1000);
    
    }

  FirebaseJson json;
  json.add("x", x);
  json.add("y", y);
  json.add("z", z);
  json.add("magnitude", magnitude);
  json.add("alert", isEarthquake ? "YES" : "NO");
  json.add("timestamp", millis());

  if (Firebase.pushJSON(fbdo, "/sensor_data", json)) {
    Serial.println("✅ Data sent to Firebase");
  } else {
    Serial.print("❌ Failed to send data: ");
    Serial.println(fbdo.errorReason());
  }

  delay(2000);
}
