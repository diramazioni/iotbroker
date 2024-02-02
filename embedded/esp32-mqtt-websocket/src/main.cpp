#include <Arduino.h>
#include <WiFi.h>
//#include <WiFiClientSecure.h>
#include <ArduinoWebsockets.h>
#include <PubSubClient.h>

#include "credentials.h"


using namespace websockets;
WebsocketsClient wsclient;
WiFiClient wifiClient;
PubSubClient client(wifiClient);

void sendMqttConnect() {
  // Construct MQTT CONNECT packet
  String connectPacket = String('\x10') + String('\x17') + String('\x00\x04') + String("MQTT") +
                         String('\x04') + String('\xC2') + String('\x00\x0F') +
                         String('\x00\x0B') + String("ESP32Client") + String('\x00\x00\x00\x00');
  wsclient.send(connectPacket);
}

void setup() {
  Serial.begin(9600);

  // Connect to Wi-Fi
  WiFi.begin(ssid_Router, password_Router);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Set up MQTT server over WSS
  wsclient.setCACert(ssl_cert);
  bool connected = wsclient.connect(ws_server_address);
  if (connected) {
    Serial.println("WebSocket connected");
    //sendMqttConnect(); // this works 101 means succesfully upgraded
                       // "GET /mqtt HTTP/1.1" 101 0 "-" "TinyWebsockets Client" 
    client.setServer(mqtt_server, mqtt_port);
    while (!client.connected()) {
      Serial.println("Attempting MQTT connection...");
      if (client.connect("ESP32Client", mqtt_username, mqtt_password)) {
        Serial.println("Connected to MQTT server");
        client.subscribe("exampleTopic");
      } else {
        Serial.print("Failed, rc=");
        Serial.print(client.state());
        Serial.println(" Retrying in 5 seconds");
        delay(5000);
      }
    }
  } else {
    Serial.println("WebSocket connection failed.");
  }    
}

void loop() {
  wsclient.poll();
  client.loop();
}
