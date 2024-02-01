#include "esp_camera.h"
#include <WiFi.h>
#include <ArduinoWebsockets.h>
// #include <algorithm>

// #include "soc/soc.h" //disable brownout problems
// #include "soc/rtc_cntl_reg.h"  //disable brownout problems

#define CAMERA_MODEL_ESP32S3_EYE
#include "camera_pins.h"
#define LED_BUILT_IN  2

// define ssid_Router, password_Router, ws_server_address
#include "credentials.h"

int wifiTimeout = 20*1000;
int interval_debug = 1000;
int interval_long = 60*60*1000;
int interval = interval_debug;

int counter = 1;

const char* endOfStream = "END_OF_STREAM";

using namespace websockets;
WebsocketsClient client;

bool ALLOWED = false;
bool DEBUG = true;


void setup() {
  Serial.begin(9600);
  delay(1000);
  //Serial.begin(115200);
  //Serial.setTimeout(2000); // wait for X sec for the serial command
  Serial.println();
  pinMode(LED_BUILT_IN, OUTPUT);
  cameraSetup();
  init_wifi();    
  init_ws();


  //disableCore0WDT();
  // WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); //disable brownout problems
}
void loop() {
  client.poll();
  /*  
  if (Serial.available() > 0) { // expires with setTimeout
    char command = Serial.read();
    serialCommand(command);
  }  
  */
  // send the image
  send_image();
}

void serialCommand(char command) {
  switch (command) {
    case 'd':      // Debug switch
      DEBUG = !DEBUG;
      Serial.println("DEBUG: " + String(DEBUG));
      client.send("CAM-DEBUG");
      if(DEBUG) {
        interval = interval_debug;
        Serial.setDebugOutput(true);
      } else {
        interval = interval_long;
        Serial.setDebugOutput(false);
      }
      break;
    case 'r':  // reset
      Serial.println("RESET");
      ESP.restart();              
      break;
    default:
      Serial.println("Unknown command");
      break;
  }
}
void send_image() {
  Serial.println("Task send image, authenticating ... ");
  while (1)  {
    if (client.available() && ALLOWED) {
      camera_fb_t * fb = NULL;
      fb = esp_camera_fb_get();
      if (fb != NULL) {
        // Send binary data in chunks
        size_t bufferSize = 1024*8;
        for (size_t i = 0; i < fb->len; i += bufferSize) {    
          size_t chunkSize = std::min(bufferSize, fb->len - i);
          client.sendBinary((const char*)(fb->buf + i), chunkSize);
        }
        client.sendBinary(endOfStream, strlen(endOfStream));
        // Send the the end of the stream as text
        //client.send(endOfStream);
        esp_camera_fb_return(fb);
        Serial.print(counter);
        Serial.println("JPEG sent");
        client.poll();
        counter++;
        delay(interval);
      } else {
        Serial.println("Camera capture failed");
        esp_camera_fb_return(fb);
        ESP.restart();
      }  
    }  else if (client.available() && !ALLOWED ) {
      Serial.print(".");
      client.poll();                                                                                                                                                                                                                                      
      delay(100);
      // wait for the authentication do nothing
    } else {
      Serial.println("WebSocket not available");
      ESP.restart();
    }
  }
  client.poll();
}
  


void init_wifi() {
  Serial.print("Connecting ");
  Serial.print(ssid_Router);
  WiFi.begin(ssid_Router, password_Router);
  // Wait for connection or timeout
  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startTime < wifiTimeout) {
    delay(500);
    Serial.print(".");
  }

  // Check if connected or timed out
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected to WiFi");
  } else {
    Serial.println("\nWiFi connection timed out");
    ESP.restart();
  }
}

void init_ws() {
  client.setCACert(ssl_cert);
  Serial.println("WebSocket: Connecting " + String(ws_server_address));
  bool connected = client.connect(ws_server_address);
  if (connected) {
    Serial.println("WebSocket connected");
    // Send the connection message
    if (client.available()) {
      String cam = "CAM-" + String(deviceString);
      client.send(cam.c_str());
      client.send("CAM-DEBUG");
    }
  } else {
    Serial.println("WebSocket connection failed.");
  }
  client.onMessage([&](WebsocketsMessage message) {
    Serial.println(message.data());
    if(message.data() == "ACK") {
      Serial.println("ALLOWED");
      ALLOWED = true;
    }
  });  
}
void cameraSetup() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG; // for streaming
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;
  
  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  // for larger pre-allocated frame buffer.
  if(psramFound()){
    Serial.print("psram device found");
    config.jpeg_quality = 10;
    config.fb_count = 2;
    config.grab_mode = CAMERA_GRAB_LATEST;
  } else {
    // Limit the frame size when PSRAM is not available
    config.frame_size = FRAMESIZE_SVGA;
    config.fb_location = CAMERA_FB_IN_DRAM;
  }

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t * s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  s->set_vflip(s, 1); // flip it back
  s->set_brightness(s, 1); // up the brightness just a bit
  s->set_saturation(s, 0); // lower the saturation

  Serial.println("Camera configuration complete!");
}
