from pyModbusTCP.server import ModbusServer, DataBank
from pyModbusTCP.client import ModbusClient
import numpy as np
from threading import Thread, Event
import time

# class server():
#     def __init__(self, 
#                  host='127.0.0.1', 
#                  port=502, 
#                  unit_id=1, 
#                  h_regs_size:int=65536, 
#                  d_inputs_size:int=65536,
#                  coils_size:int=0, 
#                  i_regs_size:int=0): # '127.0.0.1' '192.168.5.58'
        
#         self.databank = DataBank(h_regs_size = h_regs_size, 
#                                  d_inputs_size = d_inputs_size, 
#                                  coils_size = coils_size, 
#                                  i_regs_size = i_regs_size, )
#         self.server = ModbusServer(host=host, port=port, no_block=True, data_bank=self.databank)
#         self.server.start()





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
    
    def __init__(self, host='127.0.0.1', port=502, unit_id=1):
        self.client = ModbusClient(auto_open=True, auto_close=True, host=host, port=port, unit_id=1, debug=False)
        self.loop_thread = Thread(target=self.loop )
        self.loop_thread.start()

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
            if self.client.open():   
                if mode == 'C':
                    for i in range(iter):
                            self.get_list += (list(self.client.read_coils(address+i*125, 125)))
                    self.get_list += (list(self.client.read_coils(address+iter*125, last_nb)))
                else:
                    for i in range(iter):
                            self.get_list += (list(self.client.read_holding_registers(address+i*125, 125)))
                    self.get_list += (list(self.client.read_holding_registers(address+iter*125, last_nb)))
                    # print (f"\n\nget_list____________________________\n{self.get_list}\n\n")
            else:
                print("port open error")
            
            # time.sleep(0.5)
        except KeyboardInterrupt:
            print("closing modbus communication...")
            self.client.close()
        except Exception as e:
            print(f"mbus read error : {e}")
            print(f"closing modbus communication...")
            self.client.close()
        finally:
            self.client.close()
            end_time = time.time()
            # print (f"\n\nnp.array____________________________\n{np.array(self.get_list).reshape(-1, reshape).tolist()}\n\n")
            
            # print(f"mbus read : {end_time - start_time :.3f}s")
            
            # logger.logger(mission='mbus read', etc=f"{end_time - start_time :.2f}s")
            return np.array(self.get_list).reshape(-1, reshape).tolist()

        

    def write(self, address = 0, set_list = None, mode = 'HR'):
        """모드버스 송신 함수 
           address:int 부터 크기가 nb:int 인 모드버스 테이터 리스트를 덮어씀 (기본적으로 HR모드 사용)
           사용 가능 모드 mode:str in ['HR', 'DI']"""
        start_time = time.time()
        try:
            if set_list and self.client.open():
                if mode == 'DI':
                    self.client.write_multiple_coils(bits_addr=address, bits_value=set_list)
                else:
                    self.client.write_multiple_registers(regs_addr=address, regs_value=set_list)
        except Exception as e:
            print(f"mbus write error : {e}")
        finally:
            self.client.close
            end_time = time.time()
            
            # print(f"mbus write : {end_time-start_time:.3f}s")
            
            # logger.logger(mission='mbus write', etc=f"{end_time - start_time :.2f}s")
            




class plc_com(client): #, server):
    mission_enabled = False

    def __init__(self, 
                 host='127.0.0.1', 
                 port=502, 
                 unit_id=1,
                 loop_interval:float=0.5, 
                 h_regs_size:int=65536, 
                 d_inputs_size:int=65536,
                 coils_size:int=0, 
                 i_regs_size:int=0):
        
        self.loop_interval = loop_interval
        # server.__init__(self,host=host, port=port, unit_id=unit_id)
        super().__init__(host=host, port=port, unit_id=unit_id)


    def plc_check(self):
        reshape = 20
        while True:
            status = self.read(address=0, nb=reshape, reshape=reshape)
            if status:
                break
            else: print("M/B failed")
        if status[0][0] == 0 and status[0][10] == 1:
            self.mission_enabled = True
        if status[0][9]:
            self.write(address=0, set_list=[0])


    def loop(self):
        self.plc_check()
        time.sleep(self.loop_interval)

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
    modbus_inst = plc_com(loop_interval=0.5)
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

    modbus_inst.loop()