#include <Adafruit_Thermal.h>
#include <ArduinoMqttClient.h>
#include <WiFi.h>
#include <string.h>
#include "stdlib.h"
#include <EEPROM.h>
#include "secrets.h"
#include "SafeStringReader.h"

createSafeStringReader(sfReader, 32, "\r\n");

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);
const char broker[] = "broker.hivemq.com";
const int port = 1883;

const byte MAX_SIZE = 32;
char* key = "WIFI_SAVED";
String ssid = "";

struct NetworkData {
  char* key;
  char ssid[MAX_SIZE];
  char pass[MAX_SIZE];
};

void saveCredentials(const String ssid, const String pass) {
  NetworkData creds;
  creds.key = key;
  ssid.toCharArray(creds.ssid, MAX_SIZE);
  pass.toCharArray(creds.pass, MAX_SIZE);

  EEPROM.put(0, creds);
  EEPROM.commit();
}


void loadWifiCredentials() {
  // Check if wifi credentials have been saved already
  NetworkData creds;
  EEPROM.get(0, creds);
  if (creds.key != key)
    return;

  connectToWiFi(creds.ssid, creds.pass);
}

void readWifiCredentials() {
  if (sfReader.read()) {
    // Store ssid
    if (ssid.length() == 0) {
      // Store ssid length
      unsigned int len = sfReader.length();
      // Store ssid
      ssid = String(sfReader.c_str());
      Serial.println("Enter password:\n");
      return;
    }

    // Store password length + value
    unsigned int len = sfReader.length();

    // Attempt to connect to wifi (Will block all other processes)
    connectToWiFi(ssid, sfReader.c_str());
    ssid = "";
  }
}

void connectToWiFi(String ssid, String pass) {
  Serial.println("Attempting to connect with ssid=" + ssid + ", pass=" + pass);
  Serial.print("Connecting");
  int retry_count = 10;
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED && retry_count > 0) {
    Serial.print(".");
    retry_count -= 1;
    delay(5000);
  }
  if (retry_count > 0) {
    Serial.println("\nConnected!");
    saveCredentials(ssid, pass);
    connectMQTT();
    Serial.println("----------------");
  }
}

void connectMQTT() {
  if (!mqttClient.connect(broker, port)) {
    Serial.println(mqttClient.connectError());
    // Block proccess
    while (1)
      ;
  }
  mqttClient.onMessage(onMessage);
  std::string user_topic = KEY + "/" + USER;
  mqttClient.subscribe(user_topic.c_str());
  std::string all_topic = KEY + "/" + USER;
  mqttClient.subscribe(all_topic.c_str());
  Serial.println("Subscribed");
}

void onMessage(int len) {
  // PRINT MESSAGE HERE
  while (mqttClient.available()) {
    Serial.print((char)mqttClient.read());
  }
}

void setup() {
  Serial.begin(9600);
  delay(2000);
  while (!Serial) {
    ;
  }

  if (!EEPROM.begin(512)) {
    Serial.println("Failed to initialize EEPROM");
  }

  sfReader.connect(Serial);

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  loadWifiCredentials();
  Serial.println("Enter SSID:");
}

void loop() {
  readWifiCredentials();
  mqttClient.poll();
}
