from pyModbusTCP.client import ModbusClient
import time

interval_time = 0.25

def loop(interval_time = interval_time):
    c = ModbusClient(port=2502)
    while True:
        c.write_multiple_registers(11,[0,1])
        time.sleep(interval_time)
        print ("0,1")
        c.write_multiple_registers(11,[1,0])
        time.sleep(interval_time)
        print ("1,0")

loop(interval_time)

