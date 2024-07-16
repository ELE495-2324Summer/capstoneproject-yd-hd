#include <Wire.h>

// TCS34725 Constants
#define TCS34725_ADDRESS 0x29
#define TCS34725_COMMAND_BIT 0x80
#define TCS34725_ENABLE 0x00
#define TCS34725_ENABLE_PON 0x01
#define TCS34725_ENABLE_AEN 0x02
#define TCS34725_ATIME 0x01
#define TCS34725_CONTROL 0x0F
#define TCS34725_ID 0x12
#define TCS34725_CDATAL 0x14

// HC-SR04 Pins
#define TRIG_PIN 4
#define ECHO_PIN 5

// Function to write a byte to a register
void i2c_write_byte(uint8_t reg, uint8_t value) {
    Wire.beginTransmission(TCS34725_ADDRESS);
    Wire.write(TCS34725_COMMAND_BIT | reg);
    Wire.write(value);
    Wire.endTransmission();
}

// Function to read a word from a register
uint16_t i2c_read_word(uint8_t reg) {
    Wire.beginTransmission(TCS34725_ADDRESS);
    Wire.write(TCS34725_COMMAND_BIT | reg);
    Wire.endTransmission();
    Wire.requestFrom(TCS34725_ADDRESS, 2);
    uint16_t value = Wire.read() | (Wire.read() << 8);
    return value;
}

// Function to enable the TCS34725 sensor
void tcs34725_enable() {
    i2c_write_byte(TCS34725_ENABLE, TCS34725_ENABLE_PON);
    delay(3);
    i2c_write_byte(TCS34725_ENABLE, TCS34725_ENABLE_PON | TCS34725_ENABLE_AEN);
}

// Function to set integration time for the TCS34725 sensor
void tcs34725_set_integration_time(uint8_t atime) {
    i2c_write_byte(TCS34725_ATIME, atime);
}

// Function to set gain for the TCS34725 sensor
void tcs34725_set_gain(uint8_t gain) {
    i2c_write_byte(TCS34725_CONTROL, gain);
}

// Function to read RGB and Clear values from the TCS34725 sensor
void read_rgbc(uint16_t &clear, uint16_t &red, uint16_t &green, uint16_t &blue) {
    clear = i2c_read_word(TCS34725_CDATAL);
    red = i2c_read_word(TCS34725_CDATAL + 2);
    green = i2c_read_word(TCS34725_CDATAL + 4);
    blue = i2c_read_word(TCS34725_CDATAL + 6);
}

// Function to initialize the HC-SR04 sensor
void setup_hcsr04() {
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
}

// Function to measure distance using the HC-SR04 sensor
long measure_distance() {
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH);
    long distance_mm = (duration / 2) / 0.291; // Distance in mm
    return distance_mm;
}

void setup() {
    Serial.begin(115200);
    Wire.begin();

    tcs34725_enable();
    tcs34725_set_integration_time(0xD5);  // Integration time 101ms
    tcs34725_set_gain(0x00);  // Gain 1x

    setup_hcsr04();
}

void loop() {
    uint16_t clear, red, green, blue;
    read_rgbc(clear, red, green, blue);
    
    long distance_mm = measure_distance();

    Serial.print("Clear: "); Serial.print(clear);
    Serial.print(", Red: "); Serial.print(red);
    Serial.print(", Green: "); Serial.print(green);
    Serial.print(", Blue: "); Serial.print(blue);
    Serial.print(", Distance: "); Serial.print(distance_mm);

    delay(50);  // Delay 50ms
}
