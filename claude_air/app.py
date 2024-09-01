#!/home/jkitchin/.venv/bin/python
from flask import Flask, request
import jsonlines
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

import base64
import io
import datetime

app = Flask(__name__)

def b64(p):
    img = io.BytesIO()
    p.savefig(img, format='png')
    b64 = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close(p)
    return b64


@app.route('/')
def home():
    
    with jsonlines.open('/home/jkitchin/results.jsonl') as f:
        time = []
        light = []
        co2_1, co2_2 = [], []

        temp1, temp2, humidity1, humidity2 = [], [], [], []
        pressure = []

        pm1c, pm25c, pm10c = [], [], []
        pm03, pm05, pm10, pm25, pm50, pm100 = [], [], [], [], [], []

        voc1, voc2 = [], []
        
        for entry in f:
            time += [datetime.datetime.fromtimestamp(entry['t0'])]
            light += [entry['as7341']['clear']]
            
            co2_1 += [entry['sgp30']['eCO2']]
            co2_2 += [entry['scd4x']['CO2']]

            temp1 += [entry['bme688']['temperature']]
            temp2 += [entry['scd4x']['Temperature (C)']]

            humidity1 += [entry['bme688']['humidity']]
            humidity2 += [entry['scd4x']['Humidity']]

            pressure += [entry['bme688']['pressure']]

            voc1 += [entry['bme688']['voc']]
            voc2 += [entry['sgp30']['TVOC']]

            pm1c += [entry['pm25']["pm10 standard"]]
            pm25c += [entry['pm25']["pm25 standard"]]
            pm10c += [entry['pm25']["pm100 standard"]]

            pm03 += [entry['pm25']['particles 03um']]
            pm05 += [entry['pm25']['particles 05um']]
            pm10 += [entry['pm25']['particles 10um']]
            pm25 += [entry['pm25']['particles 25um']]
            pm50 += [entry['pm25']['particles 50um']]
            pm100 += [entry['pm25']['particles 100um']]
            
    p1 = plt.figure()
    plt.plot(time, light)
    plt.xlabel('time')
    plt.xticks(rotation=45)
    plt.ylabel('ambient light')
    plt.tight_layout()
    
    p2 = plt.figure()
    plt.plot(time, co2_1)
    plt.plot(time, co2_2)
    plt.xlabel('time')
    plt.xticks(rotation=45)
    plt.ylabel('CO2 (ppm)')
    plt.legend(['sgp30.eCO2', 'scd4x.CO2'])
    plt.tight_layout()

    p3, (ax1, ax2, ax3) = plt.subplots(1, 3)
    p3.set_figwidth(10, 5)
    ax1.plot(time, temp1)
    ax1.plot(time, temp2)
    ax1.legend(['bme688', 'scd4x'])
    ax1.set_xlabel('time')
    ax1.set_ylabel('Temperature (C)')
    ax1.tick_params(axis='x', labelrotation=45)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    ax2.plot(time, humidity1)
    ax2.plot(time, humidity2)
    ax2.set_xlabel('time')
    ax2.set_ylabel('% humidity')
    ax2.legend(['BME688', 'scd4x'])
    ax2.tick_params(axis='x', labelrotation=45)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    ax3.plot(time, pressure)
    ax3.set_xlabel('time')
    ax3.set_ylabel('pressure')
    ax3.tick_params(axis='x', labelrotation=45)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.tight_layout()

    vocfig = plt.figure()
    plt.plot(time, voc1)
    plt.plot(time, np.array(voc2)*1000)
    plt.xlabel('time')
    plt.xticks(rotation=45)
    plt.ylabel('VOC')
    plt.legend(['bme688', 'sgp30.TVOC * 1000'])
    
    plt.tight_layout()

    particle_fig, (ax1, ax2) = plt.subplots(1, 2)

    ax1.plot(time, pm1c, time, pm25c, time, pm10c)
    ax1.legend(['PM1.0', 'PM2.5', 'PM10'])
    ax1.set_xlabel('time')
    ax1.set_ylabel('PM concentration (standard)')
    ax1.tick_params(axis='x', labelrotation=45)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    ax2.plot(time, pm03, time, pm05, time, pm10, time, pm25, time, pm50, time, pm100)
    ax2.legend(['3um', '5um', '10u', '25um', '50um', '100um'], loc='best', ncol=2)
    ax2.set_xlabel('time')
    ax2.tick_params(axis='x', labelrotation=45)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax2.set_ylabel('particle counts')
    plt.tight_layout()
    
    return f'''<html><body>
    <h1>Light measurements</h1>
    <img src="data:image/png;base64, {b64(p1)}">

    <h1>CO<sub>2</sub></h1>
    <img src="data:image/png;base64, {b64(p2)}">

    <h1>Temperature, humidity, pressure</h1>
    <img src="data:image/png;base64, {b64(p3)}">

    <h1>VOC</h1>
    <img src="data:image/png;base64, {b64(vocfig)}">

    <h1>Particles</h1>
    <img src="data:image/png;base64, {b64(particle_fig)}">
    </body></html>'''    

def run():
    """This is used to run the server."""
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
    
if __name__ == '__main__':
    run()
