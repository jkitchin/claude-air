"""Sensors module.

Set up and run the sensors in a continous loop.
"""

import time
import numpy as np
import board
import jsonlines
import os

# https://learn.adafruit.com/adafruit-bme680-humidity-temperature-barometic-pressure-voc-gas/python-circuitpython
import adafruit_bme680
import adafruit_sgp30
# https://learn.adafruit.com/adafruit-as7341-10-channel-light-color-sensor-breakout/python-circuitpython
from adafruit_as7341 import AS7341
# https://learn.adafruit.com/adafruit-scd-40-and-scd-41/python-circuitpython
import adafruit_scd4x

# https://github.com/adafruit/Adafruit_CircuitPython_PM25
from adafruit_pm25.i2c import PM25_I2C

i2c = board.I2C()
bme688 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
sgp30.iaq_init()

scd4x = adafruit_scd4x.SCD4X(i2c)
scd4x.start_periodic_measurement()

pm25 = PM25_I2C(i2c)

as7341 = AS7341(i2c)

def one_cycle():
    """Run one cycle of collecting data from all sensors.
    """
    t0 = time.time()

    data = {'t0': t0, 'ascime': time.asctime()}

    data['bme688'] = {'temperature': bme688.temperature,
                  'humidity': bme688.humidity,
                  'pressure': bme688.pressure,
                  'voc': bme688.gas}

    eCO2, TVOC = np.mean([sgp30.iaq_measure() for i in range(20)], axis=0)
    H2, Ethanol = np.mean([sgp30.raw_measure() for i in range(20)], axis=0)
    data['sgp30'] = {'eCO2': eCO2,
                     'TVOC': TVOC,
                     'H2': H2,
                     'Ethanol': Ethanol}

    

    while True:
        if scd4x.data_ready:
        
            data['scd4x'] = {'CO2': scd4x.CO2,
                             'Temperature (C)': scd4x.temperature,
                             'Humidity': scd4x.relative_humidity}

            break
        else:
            pass

    data['pm25'] = pm25.read()

    data['as7341'] = {'clear': as7341.channel_clear}
    data['elapsed_time'] = time.time() - t0
    return data


def loop():
    """Loop function to run forever.

    It seems like it is a good idea for the sensors to stay active, rather than
    start them up cold every 15 min.

    """
    print(f'Starting loop at {time.asctime()}.')
    t0 = time.time()

    N = 0

    while True:

        # Start by getting the data
        data = one_cycle()

        # janky hook for the cli
        FLAG = os.path.expanduser('~/CLAUDE-AIR')
        if os.path.exists(FLAG):
            with jsonlines.open(os.path.expanduser('~/results.jsonl'), 'a') as f:
                f.write(data)
            os.unlink(FLAG)
            
        N += 1
        # we want to write data approximately every 15 min (900 seconds)
        elapsed_time = time.time() - t0
        if elapsed_time > (15 * 60):
            # trigger writing a file
            with jsonlines.open(os.path.expanduser('~/results.jsonl'), 'a') as f:
                f.write(data)
                print(f'Wrote a line after {N} cycles: {elapsed_time} secs')

            # reset the time and counter for the next cycle
            t0 = time.time()
            N = 0
        


if __name__ == '__main__':
    loop()
