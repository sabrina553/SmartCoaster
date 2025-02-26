from MCP3008 import MCP3008
import time



adc = MCP3008()

while True:
 
    print(adc.read(channel = 0))
    time.sleep(1) 