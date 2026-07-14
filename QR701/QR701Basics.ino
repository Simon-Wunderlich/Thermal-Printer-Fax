/*

  ThermalPrinter/QR701Basics
  Learning how to use the JP-QR701 thermal printer module with an Arduino, including QR codes generated with Python.

  For info and circuit diagrams see https://github.com/tardate/LittleArduinoProjects/tree/main/playground/ThermalPrinter/QR701Basics

 */

#include <Adafruit_Thermal.h>
#include <SoftwareSerial.h>
#include <ArduinoMqttClient.h>
#include <WiFiNINA.h>
#include <string.h>
#include <EEPROM.h>
#include "qrcode.h"
#include "SafeString.h"

createSafeStringReader(sfReader, 32, "\r\n");

WiFiClient wifiClient;
const int sigLen = 4
const char SIGNATURE[] = "WIFI";
String ssid = "";

void writeEEPROM(byte* first, int start, size_t len)
{
    for(int i = 0; i < len; i++)
    {
        EEPROM.write(i, first[i]);
    }
}

char[] readEEPROM(int start, size_t len)
{
    byte res;
    char message[len+1];
    for(int i = 0; i < len; i++)
    {
        res = EEPROM.read(i);
        meessage[i] = (char)res;
    }
    # Terminating bit - idk if this is how u do it lmao
    message[len+1] = 0;
    return message;
}

void loadWifiCredentials() {
    # Check if wifi credentials have been saved already
    const char key[] = readEEPROM(0, sigLen);
    if (strcmp(key, "WIFI") != 0)
        return;

    const int ssidLength = (int)EEPROM.read(sigLen);
    const int pwLength = (int)EEPROM.read(1 + sigLen + ssidLength);

    const char ssid[] = readEEPROM(1 + sigLen, ssidLength);
    const char pw[] = readEEPROM(2 + sigLen + ssidLength, pwLength);

    connectToWiFi(ssid, pw);
}

void readWifiCredentials() {
    if (sfReader.read()) {
        # Store ssid
        if (ssid.length() == 0) {
            # Store ssid length
            writeEEPROM(sfReader.length(), sigLen, 1);
            # Store ssid
            writeEEPROM(sfReader.c_str(), sigLen + 1, sfReader.length());
            ssid = String(sfReader);
            Serial.println("Enter password:\n");
            return;
        }

        # Store password length + value
        writeEEPROM(sfReader.length(), ssid.length() + sigLen + 1, 1);
        writeEEPROM(sfReader.c_str(), ssid.length() + sigLen + 2, sfReader.length());

        # Attempt to connect to wifi (Will block all other processes)
        connectToWiFi(ssid, sfReader);
        ssid = "";
    }
}

void connectToWiFi(String ssid, String pass) {
    while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
        Serial.print(".");
        delay(5000);
    }
}

const byte BTN_PIN = 2; // push-button
const byte RX_PIN = 5; // goes to TX on printer
const byte TX_PIN = 6; // goes to RX on printer

const int BAUDRATE = 9600;

SoftwareSerial printerSerial(RX_PIN, TX_PIN);
Adafruit_Thermal printer(&printerSerial);

volatile boolean button_enabled = false;
volatile boolean button_pressed = false;


/*
 * Set button up flag on interrupt
 */
void handleButton(void) {
  if (button_enabled) {
    button_pressed = true;
  } else {
    // inhibit the first interrupt lest it fire automatically.
    // This just seems to be an issue with my Nano clone.
    // see https://forum.arduino.cc/index.php?topic=526497.0
    button_enabled = true;
  }
}


/*
 * Command: put printer to sleep
 */
void printerSleep(void) {
  printer.sleep();
  delay(3000L);
}


/*
 * Command: wake up printer for action
 */
void printerWakeUp(void) {
  printer.wake();       // MUST wake() before printing again, even if reset
  printer.setDefault(); // Restore printer to defaults
}


/*
 * Command: run simple print job when button pressed
 */
void printerButtonPressed() {
  printerWakeUp();
  printer.justify('C');
  printer.println(F("Button Pressed"));
  printer.feed(2);
  printerSleep();
}


/*
 * Command: run a test print job
 */
void printerTest() {
  printerWakeUp();

  // Test inverse on & off
  printer.inverseOn();
  printer.println(F("Inverse ON"));
  printer.inverseOff();

  // Test character double-height on & off
  printer.doubleHeightOn();
  printer.println(F("Double Height ON"));
  printer.doubleHeightOff();

  // Set text justification (right, center, left) -- accepts 'L', 'C', 'R'
  printer.justify('R');
  printer.println(F("Right justified"));
  printer.justify('C');
  printer.println(F("Center justified"));
  printer.justify('L');
  printer.println(F("Left justified"));

  // Test more styles
  printer.boldOn();
  printer.println(F("Bold text"));
  printer.boldOff();

  printer.underlineOn();
  printer.println(F("Underlined text"));
  printer.underlineOff();

  printer.setSize('L');        // Set type size, accepts 'S', 'M', 'L'
  printer.println(F("Large"));
  printer.setSize('M');
  printer.println(F("Medium"));
  printer.setSize('S');
  printer.println(F("Small"));

  printer.justify('C');
  printer.println(F("normal\nline\nspacing"));
  printer.setLineHeight(50);
  printer.println(F("Taller\nline\nspacing"));
  printer.setLineHeight(); // Reset to default
  printer.justify('L');

  // CODE39 is the most common alphanumeric barcode:
  printer.printBarcode("LEAP", CODE39);
  printer.setBarcodeHeight(100);
  // Print UPC line on product barcodes:
  printer.printBarcode("123456789123", UPC_A);

  // Print QR code bitmap:
  printer.printBitmap(qrcode_width, qrcode_height, qrcode_data);

  printer.feed(2);
  printerSleep();
}


/*
 * Command: one-time setup
 */
void setup() {
  printerSerial.begin(BAUDRATE);
  printer.begin();
  printerSleep();

  pinMode(BTN_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(BTN_PIN), handleButton, FALLING);
  sfReader.connect(Serial)

  loadWiFiCredentials();
}


/*
 * Command: main loop
 */
void loop() {
  readWifiCredentials();
  if (button_pressed) {
    printerTest();
    // printerButtonPressed();
    button_pressed = false;
  }
}
