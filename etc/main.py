#https://tutorials-raspberrypi.com/mcp3008-read-out-analog-signals-on-the-raspberry-pi/
#https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP3004-MCP3008-Data-Sheet-DS20001295.pdf
#https://lastminuteengineers.com/fsr-arduino-tutorial/
#import global
import time, statistics, os
import matplotlib.pyplot as plt
import LEDControl

from datetime import datetime, timedelta
from MCP3008 import MCP3008
from scipy.interpolate import interp1d

import urllib, urllib.parse, threading, random
import http.client as httplib

################################################################################
def initialize():
    try:   
        global daily_water_consumption, daily_water_consumption_goal, last_mass, adc, conversion_chart, average_stable_voltage

        adc = initialize_adc()
        conversion_chart = initialize_conversion_chart()
        
        current_time = datetime.now()
        saved_variables = read_variables(current_time)
        average_stable_voltage = float(saved_variables[3])
        last_mass = float(saved_variables[2])
        daily_water_consumption, daily_water_consumption_goal = float(saved_variables[4]), 2000  # Example goal  
        LEDControl.power_on_sequence()
        
    except Exception as e:
        print(f"Error during initialization: {e}")

def read_variables(current_time):
    try:
        with open('etc/water_consumption_data', 'r') as f:
            lines = f.read().splitlines() 
            lastline = lines[-1].split(",")             
               
            if lastline[0] == current_time.strftime('%Y-%m-%d'):                
                return lastline
            else: return [0, 0, 0, 0, 0]
    except FileNotFoundError:
        return [0, 0, 0, 0, 0]  # Default values if file doesn't exist
  


def initialize_adc():
    return MCP3008()

def read_voltage():
    return adc.read(channel=0)



################################################################################
key = 'V1QKO52FOTUWHTZ2'
def thingspeak_post():
    threading.Timer(15, thingspeak_post).start()
    
    
    params = urllib.parse.urlencode({'field1': voltage,'field2': average_stable_voltage, 'key':key })
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")

    try:
        conn.request("POST", "/update", params, headers)
        response = conn.getresponse()              
        print(response.status, response.reason)
        conn.close()

    except:
        print ("connection failed")


def matlab1(i):
    plt.plot(i)
    plt.show    
    
def sensor_read(voltage, file):          
    with open("etc/"+file, "a") as f:
        data = f"{voltage}\n"
        f.write(data)

def write_consumption_data(current_time, average_stable_mass, average_stable_voltage):
    global last_recorded_time, stable_voltages, last_mass, daily_water_consumption    
    average_stable_mass = round(average_stable_mass)
    get_daily_consumption()    
    
    save_data(current_time, "%.1f" % average_stable_mass, "%.1f" % average_stable_voltage, "%1f" % daily_water_consumption)
    LEDControl.log2()    
        
    last_recorded_time = current_time
    last_mass = average_stable_mass
    
def save_data(current_time, mass, voltage, consumption):
    with open("etc/water_consumption_data", "a") as f:
        data = f"{current_time.strftime('%Y-%m-%d')}, {current_time.strftime('%H:%M:%S')}, {mass}, {voltage}, {consumption}"
        f.write('\n'+data)

################################################################################
def initialize_conversion_chart():
    global spline_model
   
    # Moved voltages and weights arrays here for clarity
                #1000        #900           #800        #700            #*600
    voltages = [968.9, 967.3, 965.0, 959.7, 953.5, 950.6, 937.6, 933.5, 923.5, 889.3, 868.6, 755.4, 559.3, 133.8, 118.6, 30.6, 23.4, 16.9, 0]
    weights = [1000, 950, 900, 850, 800, 750, 700, 650, 600, 550, 500, 450, 400, 350, 300, 250, 200, 150, 0]
    
    spline_model = interp1d(voltages, weights, kind='linear', fill_value="extrapolate")

# Function to predict weight from voltage using the spline model
def convert(voltage): 
    global spline_model
    return float(spline_model(voltage))


def voltageharmonic(voltages):
    voltage = statistics.harmonic_mean(voltages)    
    return voltage

def set_stable_voltages(voltages):
    global stable_voltages
    
    yeet = int(round(len(voltages)*0.4, 0))    
    temp = voltages[-yeet:]  # Last 100 readings
    #remove outliers from data set +/- (2%)
    tempMean = voltageharmonic(temp)    
    for i in temp:
        if abs(i-tempMean)/tempMean > 0.03:            
            temp.remove(i)
            
    stable_voltages = temp   
       
def set_stable_averages(stable_voltages):
    global average_stable_voltage, average_stable_mass, voltages

    average_stable_voltage = voltageharmonic(stable_voltages)
    average_stable_mass = convert(average_stable_voltage) 
    
    return average_stable_voltage, average_stable_mass, voltages

################################################################################
def daily(current_time):      
    date = current_time.strftime('%Y-%m-%d')
    with open('etc/water_consumption_data', 'r') as f:
        lines = f.read().splitlines()  
        fw = open('etc/Daily/'+date, 'w')                
        fw.close() 
        fa = open('etc/Daily/'+date, 'a')     
        for i in lines:
            i = i.split(",")             
            if i[0] == date:   
                data = i[1] +"," +i[2] +"," + i[3]
                fa.write(data+"\n")
         

def get_daily_consumption():
    # Implement daily consumption retrieval here
    global last_mass, average_stable_mass, daily_water_consumption    
    if (last_mass - average_stable_mass) > -10:        
        daily_water_consumption += (last_mass - average_stable_mass)        
        daily_water_consumption = round(daily_water_consumption)   
    elif (last_mass - average_stable_mass) > -200: 
        daily_water_consumption += 150
    

def reset_daily_consumption():
    global daily_water_consumption    
    daily_water_consumption = 0


def display_weight_on_LEDs(consumption_goal_percentile):
    LEDControl.weight_percentile(consumption_goal_percentile)

################################################################################
def main():
    global voltage, voltages, stable_voltage,  stable_voltages, daily_water_consumption, daily_water_consumption_goal, last_mass, current_time, average_stable_mass, last_recorded_time

    initialize()

    last_recorded_time = datetime.now()
    frequency = 0.1  # Example frequency
    stable_voltages = []
    voltages = []

    while True:    
        #matlab1(voltage)
        #thingspeak_post()
        time.sleep(frequency)
        current_time = datetime.now()
        consumption_goal_percentile = daily_water_consumption / daily_water_consumption_goal        
        
        voltage = read_voltage()
        voltages.append(voltage)   
        #sensor_read(voltage, "test1")
        
        mass_is_on_coaster = voltage > 0   
        #print(len(voltages))
        
        if current_time.hour == 0 and current_time.minute == 0:
            daily(current_time)
            reset_daily_consumption()        
        
        if mass_is_on_coaster == False:            
            voltages, stable_voltages = [], []                      
            time.sleep(10)
            continue                     
        
        if len(voltages) == 5:
            LEDControl.log2()  
            display_weight_on_LEDs(consumption_goal_percentile)          
       
        if len(voltages) == 1000: #1000, 100 test
            set_stable_voltages(voltages)
            average_stable_voltage, average_stable_mass, voltages = set_stable_averages(stable_voltages)               
            write_consumption_data(current_time, average_stable_mass, average_stable_voltage)                      
        
        if len(voltages) > 1000: 
            #6v per minute, 180v reminder.
            if len(voltages)%180 == 0:
                LEDControl.power_on_sequence() 
            time.sleep(10)      
        

if __name__ == "__main__":    
    main()