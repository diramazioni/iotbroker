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

String endOfStreamMessage = "END_OF_STREAM-" + String(deviceString);


using namespace websockets;
WebsocketsClient client;

extern TaskHandle_t loopTaskHandle;

bool ALLOWED = false;

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();
  pinMode(LED_BUILT_IN, OUTPUT);
  cameraSetup();
  init_wifi();    
  init_ws();

  //disableCore0WDT();
  // WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); //disable brownout problems
  xTaskCreateUniversal(loopTask_Cmd, "loopTask_Cmd", 8192, NULL, 1, &loopTaskHandle, 0);		//loopTask_Cmd uses core 0.
  //xTaskCreateUniversal(loopTask_Blink, "loopTask_Blink", 8192, NULL, 1, &loopTaskHandle, 0);//loopTask_Blink uses core 0.
}
//task loop uses core 1.
void loop() {

  client.poll();
  delay(1000);

}

void loopTask_Cmd(void *pvParameters) {
  Serial.println("Task send image with websocket starting ... ");

  while (1) {
    if (client.available() && ALLOWED) {
      camera_fb_t * fb = NULL;
      fb = esp_camera_fb_get();
      if (fb != NULL) {
        // Send binary data in chunks
        for (size_t i = 0; i < fb->len; i += 1024) {
          size_t chunkSize = std::min(static_cast<size_t>(1024), static_cast<size_t>(fb->len - i));          
          client.sendBinary((const char*)(fb->buf + i), chunkSize);
        }
        // Send the the end of the stream as text
        client.send(endOfStreamMessage);
        esp_camera_fb_return(fb);
        Serial.println("MJPG sent");
        delay(5000);
      } else {
        Serial.println("Camera capture failed");
        esp_camera_fb_return(fb);
        ESP.restart();
      }  
    }  else {
      Serial.println("WS client not available");
      ESP.restart();
    }
  }
  client.poll();
  delay(1000);
}
void loopTask_Blink(void *pvParameters) {
  Serial.println("Task Blink is starting ... ");
  while (1) {
    digitalWrite(LED_BUILT_IN, !digitalRead(LED_BUILT_IN));
    delay(1000);
  }
}
void init_wifi() {
  WiFi.begin(ssid_Router, password_Router);
  Serial.print("Connecting ");
  Serial.print(ssid_Router);
  while (WiFi.isConnected() != true) {
    delay(500);
    Serial.print(".");
    //WiFi.begin(ssid_Router, password_Router);
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void init_ws() {
  client.setCACert(ssl_cert);
  Serial.println("WebSocket: Connecting ");
  bool connected = client.connect(ws_server_address);
  if (connected) {
    Serial.println("WebSocket connected");
    // Send the connection message
    if (client.available()) {
      client.send('CAM-' + deviceString);
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
