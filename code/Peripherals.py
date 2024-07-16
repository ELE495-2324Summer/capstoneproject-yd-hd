import time
from smbus2 import SMBus
import serial
from jetbot import Robot
import Jetson.GPIO as GPIO

# Constants
TCS34725_ADDRESS = 0x29
TCS34725_COMMAND_BIT = 0x80
TCS34725_ENABLE = 0x00
TCS34725_ENABLE_PON = 0x01
TCS34725_ENABLE_AEN = 0x02
TCS34725_ATIME = 0x01
TCS34725_CONTROL = 0x0F
TCS34725_ID = 0x12
TCS34725_CDATAL = 0x14

class Peripherals:
    # Ultrasonic Codes
    def setGPIO(TRIG=19, ECHO=21):     
        GPIO.setmode(GPIO.BOARD)     
        GPIO.setup(TRIG, GPIO.OUT)
        GPIO.setup(ECHO, GPIO.IN)
        GPIO.output(TRIG, False)
        time.sleep(2)  
    
    def distance(TRIG=19, ECHO=21):
        # Send a 10us pulse to trigger the sensor
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        # Wait for the echo start
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        # Wait for the echo end
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        # Calculate the duration of the pulse
        pulse_duration = pulse_end - pulse_start

        # Calculate the distance
        distance = pulse_duration * 17150  # Speed of sound: 34300 cm/s, divided by 2

        return distance
    
    # Color Sensor Codes (TCS34725)
    def i2c_write_byte(bus, register, value):
        bus.write_byte_data(TCS34725_ADDRESS, TCS34725_COMMAND_BIT | register, value)
        
    def i2c_read_word(bus, register):
        data = bus.read_i2c_block_data(TCS34725_ADDRESS, TCS34725_COMMAND_BIT | register, 2)
        return data[1] << 8 | data[0]
    
    def tcs34725_enable(bus):
        Peripherals.i2c_write_byte(bus, TCS34725_ENABLE, TCS34725_ENABLE_PON)
        time.sleep(0.003)
        Peripherals.i2c_write_byte(bus, TCS34725_ENABLE, TCS34725_ENABLE_PON | TCS34725_ENABLE_AEN)
        
    def tcs34725_set_integration_time(bus, atime):
        Peripherals.i2c_write_byte(bus, TCS34725_ATIME, atime)

    def tcs34725_set_gain(bus, gain):
        Peripherals.i2c_write_byte(bus, TCS34725_CONTROL, gain)
        
    def read_rgbc_sensor1(bus):
        clear = Peripherals.i2c_read_word(bus, TCS34725_CDATAL)
        red = Peripherals.i2c_read_word(bus, TCS34725_CDATAL + 2)
        green = Peripherals.i2c_read_word(bus, TCS34725_CDATAL + 4)
        blue = Peripherals.i2c_read_word(bus, TCS34725_CDATAL + 6)
        return clear, red, green, blue
    
    def read_rgbc_arduino(arduino_serial):
        line = ""
        try:
            line = arduino_serial.readline().decode('utf-8', errors='ignore').strip()
            if line:
                clear, red, green, blue, distance = map(int, line.split(','))
                return clear, red, green, blue, distance
        except ValueError as e:
            print(f"Error parsing line: {line}, {e}")
        return None
    
    def is_white(clear, threshold=500):
        # Adjust threshold as needed
        #print(f'Clear Value: {clear}, Vs Threshold {clear > threshold}')
        return clear > threshold
