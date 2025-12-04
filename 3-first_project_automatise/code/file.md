{
  "version": 1,
  "author": "Uri Shaked",
  "editor": "wokwi",
  "parts": [
    {
      "type": "board-esp32-devkit-c-v4",
      "id": "esp",
      "top": -153.6,
      "left": -129.56,
      "attrs": {}
    },
    {
      "type": "wokwi-buzzer",
      "id": "bz1",
      "top": -170.4,
      "left": -401.4,
      "attrs": { "volume": "0.1" }
    },
    {
      "type": "wokwi-led",
      "id": "led1",
      "top": -166.8,
      "left": -274.6,
      "attrs": { "color": "red" }
    },
    {
      "type": "wokwi-resistor",
      "id": "r1",
      "top": -72.85,
      "left": -220.8,
      "attrs": { "value": "1000" }
    },
    {
      "type": "board-ssd1306",
      "id": "oled1",
      "top": -44.86,
      "left": 38.63,
      "attrs": { "i2cAddress": "0x3c" }
    },
    { "type": "wokwi-servo", "id": "servo1", "top": 55.6, "left": -307.2, "attrs": {} },
    {
      "type": "wokwi-text",
      "id": "text1",
      "top": 144,
      "left": -278.4,
      "attrs": { "text": "moteur lieé a un camera" }
    },
    {
      "type": "wokwi-text",
      "id": "text2",
      "top": -211.2,
      "left": 288,
      "attrs": { "text": "microphones " }
    },
    {
      "type": "wokwi-text",
      "id": "text3",
      "top": 124.8,
      "left": 211.2,
      "attrs": { "text": "Amplificateur" }
    },
    {
      "type": "wokwi-text",
      "id": "text4",
      "top": -67.2,
      "left": 278.4,
      "attrs": { "text": "un signal >70 dB" }
    },
    { "type": "wokwi-text", "id": "text5", "top": 76.8, "left": -115.2, "attrs": {} },
    {
      "type": "wokwi-text",
      "id": "text6",
      "top": 57.6,
      "left": 28.8,
      "attrs": { "text": "ecron de detection" }
    },
    {
      "type": "wokwi-text",
      "id": "text7",
      "top": -192,
      "left": -412.8,
      "attrs": { "text": " haut-parleur" }
    },
    {
      "type": "wokwi-text",
      "id": "text8",
      "top": -192,
      "left": -268.8,
      "attrs": { "text": "LED" }
    },
    {
      "type": "wokwi-text",
      "id": "text9",
      "top": -163.2,
      "left": 451.2,
      "attrs": { "text": "son" }
    },
    { "type": "wokwi-hc-sr04", "id": "ultrasonic1", "top": -171.3, "left": 255.1, "attrs": {} },
    { "type": "wokwi-gate-not", "id": "not1", "top": 86.4, "left": 220.8, "attrs": {} },
    {
      "type": "wokwi-resistor",
      "id": "r2",
      "top": 167.15,
      "left": 19.2,
      "attrs": { "value": "4000" }
    },
    {
      "type": "wokwi-resistor",
      "id": "r3",
      "top": 71.15,
      "left": -316.8,
      "attrs": { "value": "1000" }
    },
    {
      "type": "wokwi-resistor",
      "id": "r4",
      "top": -34.45,
      "left": -326.4,
      "attrs": { "value": "220" }
    }
  ],
  "connections": [
    [ "esp:TX", "$serialMonitor:RX", "", [] ],
    [ "esp:RX", "$serialMonitor:TX", "", [] ],
    [ "esp:GND.1", "bz1:1", "black", [ "h0" ] ],
    [ "esp:GND.1", "led1:C", "black", [ "h0" ] ],
    [ "esp:26", "r1:2", "green", [ "h0" ] ],
    [ "r1:1", "led1:A", "green", [ "v0" ] ],
    [ "esp:21", "oled1:SDA", "blue", [ "h134.4" ] ],
    [ "esp:GND.2", "oled1:GND", "black", [ "v0", "h105.6" ] ],
    [ "esp:3V3", "oled1:VCC", "#8f4814", [ "h-9.45", "v-67.2", "h220.8" ] ],
    [ "esp:22", "oled1:SCL", "white", [ "h124.8", "v9.6" ] ],
    [ "esp:GND.1", "servo1:GND", "black", [ "h-249.45", "v124.8" ] ],
    [ "esp:13", "servo1:PWM", "yellow", [ "h-239.85", "v115.2", "h57.6", "v-0.2" ] ],
    [ "ultrasonic1:GND", "esp:GND.1", "black", [ "v278.4", "h-798", "v-201.6", "h316.65" ] ],
    [ "ultrasonic1:VCC", "not1:IN", "red", [ "v153.6", "h-105.6" ] ],
    [ "not1:OUT", "r2:2", "green", [ "v67.2", "h-240" ] ],
    [ "r2:1", "esp:5V", "green", [ "v0", "h-432", "v0", "h0", "v-124.8", "h0", "v0", "h297.6" ] ],
    [ "servo1:PWM", "servo1:V+", "green", [ "h0" ] ],
    [ "servo1:V+", "r3:1", "#8f4814", [ "h-48", "v0.1" ] ],
    [ "r3:2", "esp:5V", "green", [ "v0" ] ],
    [ "esp:27", "r4:2", "green", [ "h-67.05", "v0", "h-9.6", "v0" ] ],
    [ "r4:1", "bz1:2", "green", [ "v0", "h-38.4" ] ]
  ],
  "dependencies": {}
}