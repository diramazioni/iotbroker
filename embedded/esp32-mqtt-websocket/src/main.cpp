#include <Arduino.h>
// #include <WiFi.h>
#include <WiFiClientSecure.h>
#include <WebSocketsClient.h> // include before MQTTPubSubClient.h
#include <MQTTPubSubClient.h>

#include "credentials.h"

WebSocketsClient client;
//WiFiClientSecure client;
MQTTPubSubClient mqtt;

void callback(char* topic, byte* payload, unsigned int length) {
  // Handle incoming MQTT messages here
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
  //client.setCACert(ssl_cert);
  client.beginSSL(mqtt_server, mqtt_port);
  //client.connect(mqtt_server, mqtt_port);
  // connect to mqtt broker
  Serial.println("connect to mqtt broker");
  mqtt.begin(client);
  mqtt.connect("arduino");
  if(mqtt.isConnected()) {
      Serial.println("Connected to MQTT server");
      // Subscribe to MQTT topics or perform other actions as needed
  } else {
      Serial.print("MQTT Failed");
  }
  // subscribe callback which is called when every packet has come
  mqtt.subscribe([](const String& topic, const String& payload, const size_t size) {
      Serial.println("mqtt received: " + topic + " - " + payload);
  });
}

void loop() {
  // if (!client.connected()) {
  //   reconnect();
  // }
  // should be called to trigger callbacks
  mqtt.update();
  // publish message
  mqtt.publish("/hello", "world");
  delay(1000);
}

