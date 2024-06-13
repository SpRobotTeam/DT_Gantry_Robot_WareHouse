# import sys, os
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from pyModbusTCP.server import ModbusServer, DataBank
from pyModbusTCP.client import ModbusClient
import numpy as np
from threading import Thread, Event
import time
from MW import modbus_sim
import os, pathlib

import logging
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
pathlib.Path("../logs").mkdir(parents=True, exist_ok=True)
pathlib.Path("../logs/main.log").touch
log_file_handler = logging.handlers.RotatingFileHandler(filename="../logs/main.log", 
                                    mode="a",
                                    backupCount= 3,
                                    maxBytes= 1024*1024*512,
                                    encoding='utf-8'
                                    )
log_formater = logging.Formatter("{asctime} {levelname} {filename}>{funcName} {message}", style='{')
log_file_handler.setFormatter(log_formater)
logger.addHandler(log_file_handler)


# sim = True
sim = False

class server():
    def __init__(self, 
                 host='127.0.0.1', 
                 port=502, 
                 unit_id=1, 
                 h_regs_size:int=65536, 
                 d_inputs_size:int=65536,
                 coils_size:int=0, 
                 i_regs_size:int=0): # '127.0.0.1' '192.168.5.58'
        
        self.databank = DataBank(h_regs_size = h_regs_size, 
                                 d_inputs_size = d_inputs_size, 
                                 coils_size = coils_size, 
                                 i_regs_size = i_regs_size, )
        self.server = ModbusServer(host=host, port=port, no_block=True, data_bank=self.databank)
        self.server.start()





class client():
    data_block = {
        'PC_mission_set' : [0],
        'PC_from' : [0,0,0], 
        'PC_griper_act_01' : [0], 
        'PC_reserved_01' : [0], 
        'PC_to' : [0,0,0], 
        'PC_griper_act_02' : [0], 
        'PC_reserved_02' : [0],

        'PLC_working' : [0], 
        'PLC_ready' : [0], 
        'PLC_reserved' : [0],
    }
    
    
    def __init__(self, host='127.0.0.1', port=502, unit_id=1, loop_interval = 0.5):
        self.client = ModbusClient(host=host, port=port, unit_id=1, debug=False) # auto_open=True, auto_close=True, 
        self.loop_thread = Thread(target=self.loop, daemon=True)
        self.loop_thread.start()

        self.modbus_HR = []
        self.mission_enabled = True
        self.mission_running = False
        
        self.set_list=[]
        for k,v in self.data_block.items():
            if 'PC_' in k:
                self.set_list = self.set_list + v
            else:
                break

        self.write(address=0, set_list=self.set_list)
    
    def read(self, address = 0, nb = 5*21, reshape = 21, mode = 'HR')->list:
        """모드버스 수신 함수 
           address:int 로부터 크기가 nb:int 인 모드버스 테이터 리스트를 가져옴 (기본적으로 HR모드 사용)
           사용 가능 모드 mode:str in ['HR', 'C']"""
        start_time = time.time()
        self.get_list = []
        if mode == 'C':
            nb = 8*10
            reshape = 8

        try:
            iter = nb // 125 
            last_nb = nb % 125
            
            # self.client.open()
            # time.sleep(0.2)
            # if self.client.is_open:
            connected = self.client.open()
            if connected:   
                if mode == 'C':
                    for i in range(iter):
                            self.get_list += (list(self.client.read_coils(address+i*125, 125)))
                    self.get_list += (list(self.client.read_coils(address+iter*125, last_nb)))
                else:
                    for i in range(iter):
                            recv_data = self.client.read_holding_registers(address+i*125, 125)
                            self.get_list += (list(recv_data))
                    recv_data = self.client.read_holding_registers(address+iter*125, last_nb)
                    if recv_data:
                        self.get_list += (list(recv_data))
                    # print (f"\n\nget_list____________________________\n{self.get_list}\n\n")
            else:
                print("port open error")
            
            # time.sleep(0.5)
        except KeyboardInterrupt:
            print("closing modbus communication...")
            # self.client.close()
        except Exception as e:
            print(f"mbus read error : {e}")
            print(f"closing modbus communication...")
            # self.client.close()
        finally:
            self.client.close()
            end_time = time.time()
            # print (f"\n\nnp.array____________________________\n{np.array(self.get_list).reshape(-1, reshape).tolist()}\n\n")
            
            # print(f"mbus read : {end_time - start_time :.3f}s")
            
            # logger.logger(mission='mbus read', etc=f"{end_time - start_time :.2f}s")
            if connected:
                return np.array(self.get_list).reshape(-1, reshape).tolist()
            else:
                return np.zeros(20)


        

    def write(self, address = 0, set_list = None, mode = 'HR'):
        """모드버스 송신 함수 
           address:int 부터 크기가 nb:int 인 모드버스 테이터 리스트를 덮어씀 (기본적으로 HR모드 사용)
           사용 가능 모드 mode:str in ['HR', 'DI']"""
        start_time = time.time()
        try:
            if set_list and self.client.open():
                if mode == 'DI':
                    # if address == 0:
                    #     self.client.write_multiple_coils(bits_addr=1,       bits_value=set_list[1:])
                    #     logger.info(f" address : {address}, \t set_list : {set_list}")
                    #     self.client.write_multiple_coils(bits_addr=address, bits_value=set_list[:1])
                    #     logger.info(f" address : {address}, \t set_list : {set_list}")

                    # else:
                        self.client.write_multiple_coils(bits_addr=address, bits_value=set_list)
                        # logger.info(f" address : {address}, \t set_list : {set_list}")

                else:
                    # if address == 0:
                    #     self.client.write_multiple_registers(regs_addr=1,       regs_value=set_list[1:])
                    #     logger.info(f" address : {address}, \t set_list : {set_list}")

                    #     self.client.write_multiple_registers(regs_addr=address, regs_value=set_list[:1])
                    #     logger.info(f" address : {address}, \t set_list : {set_list}")

                    # else:
                        self.client.write_multiple_registers(regs_addr=address, regs_value=set_list)
                        # logger.info(f" address : {address}, \t set_list : {set_list}")
    
        except Exception as e:
            print(f"mbus write error : {e}")
        finally:
            logger.info(f" address : {address}, \t set_list : {set_list}")
            self.client.close
            end_time = time.time()
            
            # print(f"mbus write : {end_time-start_time:.3f}s")
            
            # logger.logger(mission='mbus write', etc=f"{end_time - start_time :.2f}s")

    def plc_check(self):
        reshape = 20
        
        while True:
            time.sleep(0.1)
            try:
                self.modbus_data = self.read(address=0, nb=reshape, reshape=reshape)[0]
                recieved = True
            except IndexError or TypeError:
                recieved = False
                print("M/B failed")
                continue
            finally:
                if recieved and type(self.modbus_data)==type([]):
                    break
        
        if self.modbus_data[11] == 0 and self.modbus_data[12] == 1 and self.modbus_data[13] == 1:
            self.mission_enabled = False
            self.mission_running = False

        elif self.modbus_data[11] == 0 and self.modbus_data[12] == 1 and self.modbus_data[13] == 0:
            self.mission_enabled = True
            self.mission_running = False
            
        elif self.modbus_data[11] == 1 and self.modbus_data[12] == 0 and self.modbus_data[13] == 0:
            self.mission_enabled = False
            self.mission_running = True
            
        
        self.modbus_HR = self.modbus_data

    def loop(self):
        while True:
            self.plc_check()
            time.sleep(self.loop_interval)
            




class plc_com(client, server):
    mission_enabled = False

    def __init__(self, 
                 host='127.0.0.1', # '127.0.0.1', '192.168.0.65'
                 port=502,
                 unit_id=1,
                 loop_interval:float=0.5, 
                 h_regs_size:int=65536, 
                 d_inputs_size:int=65536,
                 coils_size:int=0, 
                 i_regs_size:int=0):
        
        self.loop_interval = loop_interval
        if sim:
            server.__init__(self,host=host, 
                            port=port, 
                            unit_id=unit_id)
            sim_Thread = Thread(target=modbus_sim.loop, args=[0.25], daemon=True)
            sim_Thread.start()


        super().__init__(host=host, port=port, unit_id=unit_id, loop_interval=loop_interval)


    


    # def loop(self):
    #     self.plc_check()
    #     time.sleep(self.loop_interval)

        # i = 0
        # while(True):
        #     # print(c.read(address=0, nb=100, reshape=10))
        #     # c.write(address=0,set_list=[i])
        #     print(modbus_inst.read(address=0, nb=100, reshape=10))
        #     modbus_inst.write(address=0,set_list=[i])
        #     time.sleep(self.loop_interval)
        #     i= i+1 if i<9 else 0
        




if __name__ == '__main__':
    # s = server(host='127.0.0.1', port=502)

    # c = client(host='127.0.0.1', port=502, unit_id=1)
    # c.write(address=0,set_list=[0])
    modbus_inst = plc_com(
        loop_interval=0.5,
        port=502 if 'nt' in os.name else 2502
        )
    # while True:
    #     c.read()
    #     time.sleep(1)
    # c.client.open()
    # c.client.is_open
    
    # i = 0
    # while(True):
    #     # print(c.read(address=0, nb=100, reshape=10))
    #     # c.write(address=0,set_list=[i])
    #     print(modbus_inst.read(address=0, nb=100, reshape=10))
    #     modbus_inst.write(address=0,set_list=[i])
    #     # time.sleep(1)
    #     i= i+1 if i<9 else 0

    # modbus_inst.loop()