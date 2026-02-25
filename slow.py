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
# Servos
# ----------------------
servo_close = PWM(Pin(19))   # activates at 15cm
servo_close.freq(50)

servo_far = PWM(Pin(21))     # activates at 30cm
servo_far.freq(50)

# Track current angles
current_angle_close = 180
current_angle_far = 0

# ----------------------
# Laser
# ----------------------
laser = Pin(23, Pin.OUT)

# ----------------------
# Servo Function
# ----------------------
def set_servo_angle_raw(servo, angle):
    min_us = 500
    max_us = 2500
    pulse_width = min_us + (angle / 180) * (max_us - min_us)
    servo.duty_ns(int(pulse_width * 1000))

def smooth_move(servo, current_angle, target_angle):
    step = 2  # smaller = smoother
    if target_angle > current_angle:
        for angle in range(current_angle, target_angle + 1, step):
            set_servo_angle_raw(servo, angle)
            sleep(0.01)
    else:
        for angle in range(current_angle, target_angle - 1, -step):
            set_servo_angle_raw(servo, angle)
            sleep(0.01)
    return target_angle

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
set_servo_angle_raw(servo_close, 180)
set_servo_angle_raw(servo_far, 0)
laser.off()

zone_state = 0   # 0 = none, 1 = 30cm zone, 2 = 15cm zone

# ----------------------
# Main Loop
# ----------------------
while True:
    try:
        distance = get_distance()

        # -------- 15 cm ZONE --------
        if distance <= 15 and zone_state != 2:
            current_angle_far = smooth_move(servo_far, current_angle_far, 90)
            current_angle_close = smooth_move(servo_close, current_angle_close, 90)
            laser.on()
            set_red()
            zone_state = 2

        # -------- 30 cm ZONE --------
        elif distance <= 30 and distance > 15 and zone_state != 1:
            current_angle_far = smooth_move(servo_far, current_angle_far, 90)
            current_angle_close = smooth_move(servo_close, current_angle_close, 180)
            laser.on()
            turn_off_leds()
            zone_state = 1

        # -------- OUTSIDE ZONE --------
        elif distance > 30 and zone_state != 0:
            current_angle_far = smooth_move(servo_far, current_angle_far, 0)
            current_angle_close = smooth_move(servo_close, current_angle_close, 180)
            laser.off()
            turn_off_leds()
            zone_state = 0

        sleep(0.1)

    except:
        turn_off_leds()
        laser.off()
        sleep(0.1)