import os
import time
import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests
from adafruit_httpserver import Server, Request, Response, POST
import neopixel
import board
import pwmio
from adafruit_motor import servo
import adafruit_bh1750

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pwm = pwmio.PWMOut(board.A2, frequency=50)
my_servo = servo.ContinuousServo(pwm, min_pulse=500, max_pulse=2450)

i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
sensor = adafruit_bh1750.BH1750(i2c)


def flap_angle(angle: int = 135, duration: int = 5):
    clock = time.monotonic() + duration
    if angle == 180:
        my_servo.throttle = 1.0
        time.sleep(0.3)
        while time.monotonic() < clock:
            my_servo.throttle = -1.0
            time.sleep(0.5)
            my_servo.throttle = 1.0
            time.sleep(0.5)
        my_servo.throttle = 0.0
        time.sleep(0.3)
        return True
    elif angle == 135:
        my_servo.throttle = 0.75
        time.sleep(0.2)
        while time.monotonic() < clock:
            my_servo.throttle = -0.75
            time.sleep(0.4)
            my_servo.throttle = 0.75
            time.sleep(0.4)
        my_servo.throttle = 0.0
        time.sleep(0.2)
        return True
    elif angle == 90:
        my_servo.throttle = 0.5
        time.sleep(0.1)
        while time.monotonic() < clock:
            my_servo.throttle = -0.5
            time.sleep(0.3)
            my_servo.throttle = 0.5
            time.sleep(0.3)
        my_servo.throttle = 0.0
        time.sleep(0.1)
        return True
    return False


def flap_freq(frequency: int = 1, duration: int = 5):
    clock = time.monotonic() + duration
    if frequency == 1:
        my_servo.throttle = 0.75
        time.sleep(0.4)
        while time.monotonic() < clock:
            my_servo.throttle = -0.75
            time.sleep(0.8)
            my_servo.throttle = 0.75
            time.sleep(0.8)
        my_servo.throttle = 0.0
        time.sleep(0.4)
        return True
    elif frequency == 2:
        my_servo.throttle = 0.75
        time.sleep(0.3)
        while time.monotonic() < clock:
            my_servo.throttle = -0.75
            time.sleep(0.6)
            my_servo.throttle = 0.75
            time.sleep(0.6)
        my_servo.throttle = 0.0
        time.sleep(0.3)
        return True
    elif frequency == 3:
        my_servo.throttle = 0.75
        time.sleep(0.2)
        while time.monotonic() < clock:
            my_servo.throttle = -0.75
            time.sleep(0.4)
            my_servo.throttle = 0.75
            time.sleep(0.4)
        my_servo.throttle = 0.0
        time.sleep(0.2)
        return True
    return False


def braitenberg_mode(duration: int = 5):
    clock = time.monotonic() + int(duration)
    while time.monotonic() < clock:
        if sensor.lux < 100:
            my_servo.throttle = -0.75
            time.sleep(0.8)
            my_servo.throttle = 0.75
            time.sleep(0.8)
        elif sensor.lux < 200:
            my_servo.throttle = -0.75
            time.sleep(0.6)
            my_servo.throttle = 0.75
            time.sleep(0.6)
        else:
            my_servo.throttle = -0.75
            time.sleep(0.4)
            my_servo.throttle = 0.75
            time.sleep(0.4)

            # Reset to start position
    my_servo.throttle = 0.0
    time.sleep(1.0)


# URLs to fetch from
TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"

print("ESP32-S2 WebClient Test")

print(f"My MAC address: {[hex(i) for i in wifi.radio.mac_address]}")

print("Available WiFi networks:")
for network in wifi.radio.start_scanning_networks():
    print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
                                             network.rssi, network.channel))
wifi.radio.stop_scanning_networks()

print(f"Connecting to {os.getenv('CIRCUITPY_WIFI_SSID')}")
wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
print(f"Connected to {os.getenv('CIRCUITPY_WIFI_SSID')}")
print(f"My IP address: {wifi.radio.ipv4_address}")

ping_ip = ipaddress.IPv4Address("8.8.8.8")
ping = wifi.radio.ping(ip=ping_ip)

# retry once if timed out
if ping is None:
    ping = wifi.radio.ping(ip=ping_ip)

if ping is None:
    print("Couldn't ping 'google.com' successfully")
else:
    # convert s to ms
    print(f"Pinging 'google.com' took: {ping * 1000} ms")

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

print("Done")

# Data for webpage
data = 1
font_family = "monospace"


def webpage():
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="Content-type" content="text/html;charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    html{{font-family: {font_family}; background-color: lightgrey;
    display:inline-block; margin: 0px auto; text-align: center;}}
      h1{{color: deeppink; width: 200; word-wrap: break-word; padding: 2vh; font-size: 35px;}}
      p{{font-size: 1.5rem; width: 200; word-wrap: break-word;}}
      .button{{font-family: {font_family};display: inline-block;
      background-color: black; border: none;
      border-radius: 4px; color: white; padding: 16px 40px;
      text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}}
      p.dotted {{margin: auto;
      width: 75%; font-size: 25px; text-align: center;}}
    </style>
    </head>
    <body>
    <title>Biorobotic fish controls</title>
    <h1>Server to control fish</h1>
    <br>
    <p class="dotted">This is a ESP32-S2 QT PY Dev Board running an HTTP server with CircuitPython.</p>
    <br>
    <p class="dotted">The current data is
    <span style="color: deeppink;">{data}</span></p><br>
    <h1>Control the LED on the Pico W with these buttons:</h1><br>
    <form accept-charset="utf-8" method="POST">
    <button class="button" name="LED ON" value="ON" type="submit">LED ON</button></a></p></form>
    <p><form accept-charset="utf-8" method="POST">
    <button class="button" name="LED OFF" value="OFF" type="submit">LED OFF</button></a></p></form>
    <h1>Party?</h>
    <p><form accept-charset="utf-8" method="POST">
    <button class="button" name="party" value="party" type="submit">PARTY!</button></a></p></form>
    </body></html>
    """
    return html


pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)


@server.route("/")
def base(request: Request):
    return Response(request, f"{webpage()}", content_type='text/html')


@server.route("/change-neopixel-color/<r>/<g>/<b>")
def change_neopixel_color_handler_url_params(
        request: Request, r: str = "0", g: str = "0", b: str = "0"
):
    """Changes the color of the built-in NeoPixel using URL params."""
    pixel.fill((int(r), int(g), int(b)))

    return Response(request, f"Changed NeoPixel to color ({r}, {g}, {b})")


@server.route("/get-light")
def get_light(request: Request):
    return Response(request, f"{round(sensor.lux, 2)}")


@server.route("/exp_1/<angle>/<duration>")
def experiment_1(request: Request, angle: int = 180, duration: int = 5):
    angle = int(angle)
    duration = int(duration)

    success = flap_angle(angle, duration)

    resp = f"Could not start experiment 1. Angle {angle} is not an option."
    if success:
        resp = f"Started experiment 1 with angle {angle}."
    return Response(request, resp)


@server.route("/exp_2/<frequency>/<duration>")
def experiment_2(request: Request, frequency: int = 1, duration: int = 5):
    frequency = int(frequency)
    duration = int(duration)

    success = flap_freq(frequency, duration)

    resp = f"Could not start experiment 1. Frequency level {frequency} is not an option."
    if success:
        resp = f"Started experiment 1 with frequency level {frequency}."
    return Response(request, resp)


@server.route("/exp_3/<duration>")
def experiment_3(request: Request, duration: int = 5):
    braitenberg_mode(duration)
    return Response(request, f"Running Braitenberg fish")


server.serve_forever(str(wifi.radio.ipv4_address))