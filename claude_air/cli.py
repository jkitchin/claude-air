#!/home/jkitchin/.venv/bin/python
import jsonlines
import os
import pathlib
import time
from rich import print


def cli():

    FLAG = pathlib.Path(os.path.expanduser('~/CLAUDE-AIR'))
    FLAG.touch()

    # This should get deleted by sensors
    while FLAG.exists():
        time.sleep(1)

    with jsonlines.open(os.path.expanduser('~/results.jsonl'), 'r') as f:
        for entry in f:
            data = entry


    print('[bold magenta]Claude Air Monitor[/bold magenta]')
    print(time.asctime())
    print()
    print('[bold magenta]# BME688 sensor[/bold magenta]')
    print(f'T={data["bme688"]["temperature"]:1.1f} C\t'
          f'VOC={data["bme688"]["voc"]:1.2f}\t'
          f'Humidity={data["bme688"]["humidity"]:1.2f}\t'
          f'P={data["bme688"]["pressure"]:1.2f}')
    print()

    # # https://pypi.org/project/adafruit-circuitpython-sgp30/
    print('[bold magenta]# sgp30 sensor[/bold magenta]')

    print(f'eCO2={data["sgp30"]["eCO2"]:1.0f} ppm\t'
          f' TVOC={data["sgp30"]["TVOC"]:1.0f} ppb\t'
          f'H2={data["sgp30"]["H2"]:1.0f}\t'
          f'Ethanol={data["sgp30"]["Ethanol"]:1.0f}')
    print()


    print('[bold magenta]# scd40 sensor[/bold magenta]')


    print(f'CO2: {data["scd4x"]["CO2"]:0.1f} ppm  '
          f'Temperature: {data["scd4x"]["Temperature (C)"]:0.1f} C '
          f'Humidity: {data["scd4x"]["Humidity"]:0.1f}%')
    print()
    print('[bold magenta]# Particle counts[/bold magenta]')
    print("Concentration Units (standard)")
    print("---------------------------------------")
    print(
        f'PM1.0: {data["pm25"]["pm10 standard"]}\t'
        f'PM2.5: {data["pm25"]["pm25 standard"]}\t' 
        f'PM10: {data["pm25"]["pm100 standard"]}')
    print("Concentration Units (environmental)")
    print("---------------------------------------")
    print(
        f'PM1.0: {data["pm25"]["pm10 env"]}\t'
        f'PM2.5: {data["pm25"]["pm25 env"]}\t'
        f'PM10: {data["pm25"]["pm100 env"]}')
    print("---------------------------------------")
    print("Particles > 0.3um / 0.1L air:", data["pm25"]["particles 03um"])
    print("Particles > 0.5um / 0.1L air:", data["pm25"]["particles 05um"])
    print("Particles > 1.0um / 0.1L air:", data["pm25"]["particles 10um"])
    print("Particles > 2.5um / 0.1L air:", data["pm25"]["particles 25um"])
    print("Particles > 5.0um / 0.1L air:", data["pm25"]["particles 50um"])
    print("Particles > 10 um / 0.1L air:", data["pm25"]["particles 100um"])
    print("---------------------------------------")
    print()

    print('[bold magenta]# Light AS7341 sensor[/bold magenta]')
    print(f'clear={data["as7341"]["clear"]}')
    print()

