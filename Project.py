import requests
import bme680
import blinkt
import time
from Adafruit_IO import *

aio = Client('BolzanoBus',"aio_NPsN99dztuufovvDx1T76Wp8v9x6")

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except (RuntimeError, IOError):
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

start_time = time.time()
curr_time = time.time()
burn_in_time = 15

try:
    while curr_time - start_time < burn_in_time:
        curr_time = time.time()
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            print('Gas: {0} Ohms'.format(gas))
            time.sleep(1)
except (RuntimeError, IOError):
    exit

openweatherkey = "d30f33b20a346747fac155bfbc7839bd"

api_key = openweatherkey
url = "https://api.openweathermap.org/data/2.5/onecall"

ow_dict = { 'lat': 46.498113, 'lon': 11.35478, 'appid': api_key, 'units': 'metric' }

# define baselines for both gas and humidity values
gas_baseline = 50000.0
hum_baseline = 40.0
# weight of the humidity on the total score
hum_weight = 0.25
# define the optimal value and the optimal range
opt_temp = 22.0
low_bound = 20.0
up_bound = 24.0
# get values for humidity and gas and calculate the offsets from the base values
gas_resistance = 50000
humidty = 40
try:
    while True:
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas_resistance = sensor.data.gas_resistance
            print('Gas: {0} Ohms'.format(gas_resistance))
            humidity = sensor.data.humidity
        aio.send("bb.hum",humidity)
        gas_offset = gas_resistance - gas_baseline
        hum_offset = humidity - hum_baseline
        # calculate humidity score
        if hum_offset > 0:
            hum_score = (1 - hum_offset/(100-hum_baseline))
        else:
            hum_score = humidity / hum_baseline
        hum_score *= hum_weight
        # calculate gas score
        gas_score = 1.0 - hum_weight
        if gas_offset < 0:
            gas_score = (gas_resistance/gas_baseline) * (1.0 - hum_weight)

        # showing values
        print("Gas score: ", gas_score)
        print("Humidity score: ", hum_score)
        # calculate and show the indoor air quality score
        ia_quality_score = hum_score + gas_score
        print("Total air score: ", ia_quality_score)

        # set base score for temperature
        temp_score = 1.0
        # get values for indoor and outdoor temperatures plus the weather condition
        response = requests.get(url, params=ow_dict)

        if 200 <= response.status_code < 400:
            data = response.json()
            temperature = data["current"]["temp"]
            weather = data["current"]["weather"][0]["main"]
            curr_in_temp = temperature
            if sensor.get_sensor_data() and sensor.data.heat_stable:
                curr_in_temp = sensor.data.temperature
            curr_out_temp = temperature
            curr_weather_cond = weather
            aio.send("bb.temp",curr_in_temp)
            # calculate temperature score
            if curr_weather_cond != 'Rainy':
                if curr_in_temp < low_bound or curr_in_temp > up_bound:
                    if curr_in_temp - opt_temp > 0:
                        if low_bound < curr_out_temp < curr_in_temp:
                            temp_offset = curr_in_temp - curr_out_temp
                            temp_score = (curr_out_temp-temp_offset)/curr_out_temp
                    else:
                        if curr_in_temp < curr_out_temp < up_bound:
                            temp_score = curr_in_temp / curr_out_temp
        else:
            print('Unsuccessful request')
            print(response)

        # weight of the temperature and ia quality score on the total score
        temp_weight = 0.40
        ia_weight = 0.60
        temp_score *= temp_weight
        ia_quality_score *= (1.0 - temp_weight)
        print("Temperature score: ", temp_score)
        tot_score = temp_score + ia_quality_score
        aio.send("bb.score",tot_score*100)
        print("Total score: ",tot_score)

        # select led color based on score
        if 0.75 < tot_score < 1.0:
            color = [0,0,255]
        elif 0.5 < tot_score <= 0.75:
            color = [255,0,255]
        else:
            color = [255,0,0]

        blinkt.set_clear_on_exit(True)
        blinkt.set_all(color[0],color[1],color[2],0.1)
        blinkt.show()
        time.sleep(10)
except KeyboardInterrupt:
    print('Bye')
except ThrottlingError:
    print('Error from Adafruit IO')