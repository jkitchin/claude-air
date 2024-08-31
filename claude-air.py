#!/home/jkitchin/.venv/bin/python
import board

# https://learn.adafruit.com/adafruit-bme680-humidity-temperature-barometic-pressure-voc-gas/python-circuitpython
import adafruit_bme680
import adafruit_sgp30
# https://learn.adafruit.com/adafruit-as7341-10-channel-light-color-sensor-breakout/python-circuitpython
from adafruit_as7341 import AS7341
# https://learn.adafruit.com/adafruit-scd-40-and-scd-41/python-circuitpython
import adafruit_scd4x

# https://github.com/adafruit/Adafruit_CircuitPython_PM25
from adafruit_pm25.i2c import PM25_I2C

import time
import os
import jsonlines

i2c = board.I2C()

t0 = time.time()

bme688 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

data = {'t0': t0, 'ascime': time.asctime()}

data['bme688'] = {'temperature': bme688.temperature,
                  'humidity': bme688.humidity,
                  'pressure': bme688.pressure,
                  'voc': bme688.gas}

print(f'T={bme688.temperature:1.1f}C, VOC={bme688.gas:1.2f}, Humidity={bme688.humidity:1.2f}, P={bme688.pressure:1.2f}')

# https://pypi.org/project/adafruit-circuitpython-sgp30/
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

eCO2, TVOC = sgp30.iaq_measure()

data['sgp30'] = {'eCO2': eCO2,
                 'TVOC': TVOC}

print("eCO2 = %d ppm \t TVOC = %d ppb" % (eCO2, TVOC))


pm25 = PM25_I2C(i2c)
aqdata = pm25.read()

print()
print("Concentration Units (standard)")
print("---------------------------------------")
print(
    "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
    % (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"])
)
print("Concentration Units (environmental)")
print("---------------------------------------")
print(
    "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
    % (aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"])
)
print("---------------------------------------")
print("Particles > 0.3um / 0.1L air:", aqdata["particles 03um"])
print("Particles > 0.5um / 0.1L air:", aqdata["particles 05um"])
print("Particles > 1.0um / 0.1L air:", aqdata["particles 10um"])
print("Particles > 2.5um / 0.1L air:", aqdata["particles 25um"])
print("Particles > 5.0um / 0.1L air:", aqdata["particles 50um"])
print("Particles > 10 um / 0.1L air:", aqdata["particles 100um"])
print("---------------------------------------")

data['pm25'] = aqdata



as7341 = AS7341(i2c)
print("F1 - 415nm/Violet  %s" % as7341.channel_415nm)
print("F2 - 445nm//Indigo %s" % as7341.channel_445nm)
print("F3 - 480nm//Blue   %s" % as7341.channel_480nm)
print("F4 - 515nm//Cyan   %s" % as7341.channel_515nm)
print("F5 - 555nm/Green   %s" % as7341.channel_555nm)
print("F6 - 590nm/Yellow  %s" % as7341.channel_590nm)
print("F7 - 630nm/Orange  %s" % as7341.channel_630nm)
print("F8 - 680nm/Red     %s" % as7341.channel_680nm)
print("F9 - nir           %s" % as7341.channel_nir  )
print("F10- clear         %s" % as7341.channel_clear)

data['as7341'] = {'clear': as7341.channel_clear}

scd4x = adafruit_scd4x.SCD4X(i2c)

scd4x.start_periodic_measurement()

while True:
    if scd4x.data_ready:
        print("CO2: %d ppm" % scd4x.CO2)
        print("Temperature: %0.1f *C" % scd4x.temperature)
        print("Humidity: %0.1f %%" % scd4x.relative_humidity)

        data['scd4x'] = {'CO2': scd4x.CO2,
                         'Temperature (C)': scd4x.temperature,
                         'Humidity': scd4x.relative_humidity}
        print()
        break
    else:
        time.sleep(0.1)

with jsonlines.open(os.path.expanduser('~/results.jsonl'), 'a') as f:
    f.write(data)
