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

const int sigLen = 4;
const char SIGNATURE[] = "WIFI";
String ssid = "";

void writeEEPROM(const char* first, int start, size_t len)
{
    for (int i = 0; i < len; i++)
 {
      EEPROM.write(i, first[i]);
  }
}

char* readEEPROM(int start, size_t len)
{
  byte res;
  char* message = (char*)malloc(len * sizeof(char));;
  for (int i = 0; i < len; i++)
  {
    res = EEPROM.read(i);
    *(message + i) = (char)res;
  }
  return message;
}

void loadWifiCredentials() {
  // Check if wifi credentials have been saved already
  const char* key = readEEPROM(0, sigLen);
  if (strcmp(key, "WIFI") != 0)
  return;
  
  const int ssidLength = (int)EEPROM.read(sigLen);
  const int pwLength = (int)EEPROM.read(1 + sigLen + ssidLength);
  
  const char* ssid = readEEPROM(1 + sigLen, ssidLength);
  const char* pw = readEEPROM(2 + sigLen + ssidLength, pwLength);
  
  connectToWiFi(ssid, pw);
}

void readWifiCredentials() {
  if (sfReader.read()) {
    // Store ssid
    if (ssid.length() == 0) {
      // Store ssid length
      unsigned int len = sfReader.length();
      writeEEPROM((char*)&len, sigLen, 1);
      // Store ssid
      writeEEPROM(sfReader.c_str(), sigLen + 1, sfReader.length());
      ssid = String(sfReader.c_str());
      Serial.println("Enter password:\n");
      return;
    }
    
    // Store password length + value
    unsigned int len = sfReader.length();
    writeEEPROM((char*)&len, ssid.length() + sigLen + 1, 1);
    writeEEPROM(sfReader.c_str(), ssid.length() + sigLen + 2, sfReader.length());
    
    // Attempt to connect to wifi (Will block all other processes)
    connectToWiFi(ssid, sfReader.c_str());
    ssid = "";
  }
}

void connectToWiFi(String ssid, String pass) {
  int retry_count = 10;
  while (WiFi.begin(ssid, pass) != WL_CONNECTED && retry_count > 0) {
    Serial.print(".");
    retry_count -= 1;
    delay(5000);
  }
  if (retry_count > 0) {
    writeEEPROM(SIGNATURE, 0, sigLen);
  }
}

void connectMQTT() {
  if (!mqttClient.connect(broker, port)) {
    Serial.println(mqttClient.connectError());
    // Block proccess
    while(1);
  }
  mqttClient.onMessage(onMessage);
  mqttClient.subscribe(KEY + "/" + USER);
  mqttClient.subscribe(KEY + "/all");
}

void onMessage(int len) {
  // PRINT MESSAGE HERE
  while(mqttClient.available()) {
    Serial.print((char)mqttClient.read());
  }
}

void setup() {
    sfReader.connect(Serial);

    loadWifiCredentials();
}


//Command: main loop

void loop() {
    readWifiCredentials();
    mqttClient.poll();
}
