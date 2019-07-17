#include <inttypes.h>

// The time between subsequent samples, in ms
#define PERIOD 1
// The delay between input and output
#define MAX_DELAY 1000

#define OUTPIN 9

const size_t bufferlen = (int)(MAX_DELAY/PERIOD)+1;

uint8_t signal_buffer[bufferlen];

void setup() {
  Serial.begin(9600);
  while (!Serial);
  pinMode(OUTPIN, OUTPUT);
  Serial.print("max");
  Serial.println(MAX_DELAY);
}

void loop() {
  static uint32_t last_run = 0;
  static uint32_t frame = 0;

  if (millis() - last_run < PERIOD) {
    return;
  } else {
    last_run = millis();
  }

  static uint32_t delay = 0;
  static int32_t offset = 0;

  if (Serial.available()) {
    static char buf[8];
    uint8_t wr = Serial.readBytesUntil('\n', buf, 8);
    buf[wr] = '\0';
    int setting = atoi(buf);
    Serial.print("read");
    Serial.println(setting);
    
    if (setting < 0 || setting > MAX_DELAY) {
      Serial.println("OOR");
    } else {
      delay = setting;
      offset = delay/PERIOD;
      Serial.print("offset");
      Serial.println(offset);
    }
  }

  

  
  uint8_t inval = analogRead(A0)/4;
  signal_buffer[frame % bufferlen] = inval;

  uint8_t outval = signal_buffer[((int32_t)frame - offset)%bufferlen];
  analogWrite(OUTPIN, outval);
  frame++;
}

