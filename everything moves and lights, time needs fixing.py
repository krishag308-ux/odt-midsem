from machine import Pin, PWM, time_pulse_us
from time import sleep_us, sleep
import neopixel

# ----------------------
# Ultrasonic Sensor
# ----------------------
trig = Pin(5, Pin.OUT)
echo = Pin(18, Pin.IN)

# ----------------------
# NeoPixel
# ----------------------
NUM_LEDS = 8
np = neopixel.NeoPixel(Pin(4), NUM_LEDS)

# ----------------------
# Servo Motors
# ----------------------
servo1 = PWM(Pin(19))
servo1.freq(50)

servo2 = PWM(Pin(21))
servo2.freq(50)

# ----------------------
# Laser
# ----------------------
laser = Pin(23, Pin.OUT)

# ----------------------
# Servo Control Function
# ----------------------
def set_servo_angle(servo, angle):
    min_us = 500
    max_us = 2500
    pulse_width = min_us + (angle / 180) * (max_us - min_us)
    servo.duty_ns(int(pulse_width * 1000))

# ----------------------
# Distance Function
# ----------------------
def get_distance():
    trig.off()
    sleep_us(2)
    trig.on()
    sleep_us(10)
    trig.off()

    duration = time_pulse_us(echo, 1, 30000)
    distance = (duration * 0.0343) / 2
    return distance

# ----------------------
# LED Functions
# ----------------------
def set_red():
    for i in range(NUM_LEDS):
        np[i] = (255, 0, 0)
    np.write()

def turn_off_leds():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()

# ----------------------
# Initial State
# ----------------------
set_servo_angle(servo1, 0)
set_servo_angle(servo2, 0)
laser.off()

activated = False

# ----------------------
# Main Loop
# ----------------------
while True:
    try:
        distance = get_distance()

        if distance <= 15 and not activated:
            set_red()
            set_servo_angle(servo1, 90)
            set_servo_angle(servo2, 90)
            laser.on()
            activated = True

        elif distance > 15 and activated:
            turn_off_leds()
            set_servo_angle(servo1, 0)
            set_servo_angle(servo2, 0)
            laser.off()
            activated = False

        sleep(0.1)

    except:
        turn_off_leds()
        laser.off()
        sleep(0.1)