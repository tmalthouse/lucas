/*
  Digital Pot Control

  This example controls an Analog Devices AD5206 digital potentiometer.
  The AD5206 has 6 potentiometer channels. Each channel's pins are labeled
  A - connect this to voltage
  W - this is the pot's wiper, which changes when you set it
  B - connect this to ground.

  The AD5206 is SPI-compatible,and to command it, you send two bytes,
  one with the channel number (0 - 5) and one with the resistance value for the
  channel (0 - 255).

  The circuit:
    All A pins  of AD5206 connected to +5V
    All B pins of AD5206 connected to ground
    An LED and a 220-ohm resisor in series connected from each W pin to ground
    CS - to digital pin 10  (SS pin)
    SDI - to digital pin 11 (MOSI pin)
    CLK - to digital pin 13 (SCK pin)

  created 10 Aug 2010
  by Tom Igoe

  Thanks to Heather Dewey-Hagborg for the original tutorial, 2005

*/


// inslude the SPI library:
#include <SPI.h>
#include <inttypes.h>
#include <string.h>


// set pin 10 as the slave select for the digital pot:
const int slaveSelectPin = 10;

// We don't want to connect to digipot unless it's powered
const int safetyLatchPin = 11;

const char OK = 'A';
const char PWR_ERR = 'B';
const char STR_ERR = 'C';

struct pot_setting {
  uint8_t chan;
  uint8_t val;
  uint8_t status;
};

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ;//nop
  }
  // set the slaveSelectPin as an output:
  pinMode(slaveSelectPin, OUTPUT);

  pinMode(safetyLatchPin, INPUT);
  // initialize SPI:
  SPI.begin();
  Serial.println(OK);

}

void loop() {
  static char buf[8];

  if (Serial.available() > 0) {
    get_serialdata(buf);
  } else {
    return;
  }

  struct pot_setting setting = decode_string(buf);
  if (!setting.status) {
    Serial.println(STR_ERR);
    return;
  }

  digitalPotWrite(setting.chan, setting.val);
  digitalPotWrite(setting.chan, setting.val);
  Serial.println(OK);
  return;

}

void get_serialdata(char *buf) {
  int len = Serial.readBytesUntil('\n', buf, 10);
  // Make sure to null-terminate the read string
  buf[2] = 0x0;
}

struct pot_setting decode_string(char *buf) {
  struct pot_setting set = {0, 0, 1};
  int chan, val;


  chan = (uint8_t)buf[0];
  val = (uint8_t)buf[1];
  if (chan < 0 || chan >= 6) {
    set.status = 0;
  } else {
    set.chan = chan;
  }
  if (val < 0 || val > 255) {

    set.status = 0;
  } else {
    set.val = val;
  }

  return set;
}


void digitalPotWrite(int address, int value) {
  // take the SS pin low to select the chip:
  digitalWrite(slaveSelectPin, LOW);
  //  send in the address and value via SPI:
  SPI.transfer(address);
  SPI.transfer(value);
  // take the SS pin high to de-select the chip:
  digitalWrite(slaveSelectPin, HIGH);
}

