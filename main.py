# import modules
import bme280
import network
import socket
from time import sleep
from machine import Pin, I2C
import machine

ssid = 'wifi name'  # Your network name
password = 'wifi password'  # Your WiFi password

# initialize I2C
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)


def connect():
    # Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip


def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection


def webpage_json(tmp, prs, hum):
    json = {
        'temperature': f'{tmp}',
        'humidity': f'{hum}',
        'pressure': f'{prs}'
            }
    return str(json)


def serve(connection):
    # Start a web server

    while True:
        bme = bme280.BME280(i2c=i2c)
        temp = bme.values[0]
        pressure = bme.values[1]
        humidity = bme.values[2]
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        json = webpage_json(temp, pressure, humidity)
        client.send(json)
        client.close()


try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
