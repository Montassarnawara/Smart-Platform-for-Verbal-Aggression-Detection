#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h>
#include <vector>

// ------------------------
// WIFI
// ------------------------
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// ------------------------
// OLED
// ------------------------
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ------------------------
// Pins
// ------------------------
const int LED_PIN = 26;
const int BUZZER_PIN = 27;
const int SERVO_PIN = 13;

Servo camera_servo;

// ------------------------
// Setup
// ------------------------
void setup() {
  Serial.begin(115200);

  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  Wire.begin(21, 22);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("Erreur OLED"));
    while (true);
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Demarrage...");
  display.display();

  // Connexion WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" Connecté au Wi-Fi");

  // Servo
  camera_servo.setPeriodHertz(50);
  camera_servo.attach(SERVO_PIN, 500, 2400);
  camera_servo.write(90);
}

// ------------------------
// Loop
// ------------------------
void loop() {
  std::vector<int> levels;

  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("📡 Collecte...");

  for (int i = 0; i < 10; i++) {
    int sound_level = random(30, 110);
    Serial.println("🔊 Niveau sonore : " + String(sound_level));
    levels.push_back(sound_level);
    delay(100);
  }

  int danger_percent = sendAlertToServer(levels);
  reaction(danger_percent);

  delay(4000); // attente entre chaque envoi
}

// ------------------------
// Envoi à l'API + lecture réponse
// ------------------------
int sendAlertToServer(const std::vector<int>& levels) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin("https://esp32-alert-api-3.onrender.com/danger-alert");
    http.addHeader("Content-Type", "application/json");

    DynamicJsonDocument doc(512);
    JsonArray arr = doc.createNestedArray("levels");
    for (int l : levels) arr.add(l);

    String payload;
    serializeJson(doc, payload);
    Serial.println("📤 Envoi JSON : " + payload);

    int response = http.POST(payload);
    int danger_pct = 0;

    if (response > 0) {
      String body = http.getString();
      Serial.println("📥 Réponse : " + body);

      DynamicJsonDocument resDoc(256);
      DeserializationError err = deserializeJson(resDoc, body);
      if (!err && resDoc.containsKey("percent")) {
        danger_pct = resDoc["percent"];
      } else {
        Serial.println("⚠️ Erreur JSON");
      }
    } else {
      Serial.println("❌ Erreur HTTP : " + String(response));
    }

    http.end();
    return danger_pct;
  }
  return 0;
}

// ------------------------
// Réaction
// ------------------------
void reaction(int danger_pct) {
  display.setCursor(0, 20);
  display.print("Danger: ");
  display.println(danger_pct);

  if (danger_pct < 45) {
    digitalWrite(LED_PIN, HIGH);
    tone(BUZZER_PIN, 300, 500);
    camera_servo.write(90);
    display.println("⚠️ Danger faible");
  }
  else if (danger_pct < 70) {
    digitalWrite(LED_PIN, HIGH);
    tone(BUZZER_PIN, 600, 700);
    camera_servo.write(60);
    display.println("🚨 Danger modéré");
  }
  else {
    digitalWrite(LED_PIN, HIGH);
    tone(BUZZER_PIN, 1000, 1000);
    camera_servo.write(30);
    display.println("🚔 Danger élevé");
    display.println("📩 SMS envoyé !");
  }

  display.display();
  delay(1000);
  resetSystem();
}

// ------------------------
// Réinitialisation
// ------------------------
void resetSystem() {
  digitalWrite(LED_PIN, LOW);
  noTone(BUZZER_PIN);
  camera_servo.write(90);
}
