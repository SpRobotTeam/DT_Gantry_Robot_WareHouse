# import sys, os
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from WCS.Area_mng import area_manager
import math
import numpy as np
import MW.PLC_com as PLC_com
import time

PORT = 502

class zone_manager():
    def __init__(self, 
                 zone_properties_dict
                 ):
        if not len(zone_properties_dict['container'].keys()):
            self.CONTAINER = {
                                'name'      : 'default',
                                'length'    : 300, 
                                'width'     : 200, 
                                'height'    : 200,
                                'gap'       : 200
                                }
        else:
            self.CONTAINER = zone_properties_dict['container']
        
        self.Modbus_inst = PLC_com.plc_com(port = PORT)
        self.Area_dict = {}
        self.ZONE_NAME = zone_properties_dict['Zone_name']

    
    def add_area(self, area_properties_dict):
        # self.exec()
        
        Area_name = area_properties_dict['Area_name']
        self.Area_dict[Area_name] = \
            locals()[Area_name] = \
                area_manager(
                    Area_name=Area_name,
                    origin_point=area_properties_dict['origin'],  
                    col_block=area_properties_dict['col'], 
                    row_block=area_properties_dict['row'], 
                    height_block=area_properties_dict['heigth'], 
                    grid_type=area_properties_dict['grid_type']
                    )
                                


    def add_default_areas(self,
                          area_length=None,
                          area_width=None,
                          area_height=None,
    ):
        if not area_length:
            area_length = 12000
        if not area_width:
            area_width  = 7000
        if not area_height:
            area_height = 1600

        self.COL_TOTAL    = area_length//self.CONTAINER['length'] # 34
        self.ROW_TOTAL    = area_width //self.CONTAINER['width']  # 31        
        self.HEIGTH_TOTAL = area_height//self.CONTAINER['height'] # 8
        
        Gantry = area_manager(   
                                    # Gantry, 
                                    # area_manager,
                                    Area_name="Gantry",   
                                    origin_point=[0,math.ceil(self.ROW_TOTAL/2),0], 
                                    col_block=1,  
                                    row_block=1 , 
                                    height_block=self.HEIGTH_TOTAL, 
                                    grid_type='r'
                                    )
        self.Area_dict['Gantry'] = Gantry

        In      = area_manager(
                                    # In,
                                    # area_manager,
                                    Area_name="In",     
                                    origin_point=[0,self.ROW_TOTAL,0],  
                                    col_block=1,  
                                    row_block=1, 
                                    height_block=self.HEIGTH_TOTAL, 
                                    grid_type='r'
                                    )
        self.Area_dict['In'] = In

        Out     = area_manager(
                                    # Out,
                                    # area_manager,
                                    Area_name="Out",    
                                    origin_point=[0,0,0], 
                                    col_block=1,  
                                    row_block=1, 
                                    height_block=self.HEIGTH_TOTAL, 
                                    grid_type='r'
                                    )
        self.Area_dict['Out'] = Out

        Area_01 = area_manager(
                                    # Area_01,
                                    # area_manager,
                                    Area_name="Area_01",
                                    origin_point=[1,0,0],  
                                    col_block=self.COL_TOTAL-1, 
                                    row_block=self.ROW_TOTAL, 
                                    height_block=self.HEIGTH_TOTAL, 
                                    grid_type='r'
                                    )
        self.Area_dict['Area_01'] = Area_01

        return self # self.Area_dict
    


    def optimal_pos_find(self, Area_name, outbound_freq, priority, lot=None):  # origin=[0,0],
        '''
        구역 특성과 상품의 outbound_freq, priority에 따라 적절한 위치 탐색

        현재 First-Fit 과 유사한 방식 사용
        '''
        iter = 0
        if outbound_freq[0].lower() == 'h':
        # global_loc = [0,0,0]
            for x in range(self.Area_dict[Area_name].COL):
                for y in range(self.Area_dict[Area_name].ROW):
                    if len(self.Area_dict[Area_name].grid[x][y]) == 0:
                        iter += 1
                        if iter >= priority:
                            # return[x,y]
                            return [
                                x ,# + self.Area_dict[Area_name].ORIGIN_POINT[0],
                                y ,# + self.Area_dict[Area_name].ORIGIN_POINT[1],
                                len(self.Area_dict[Area_name].grid[x][y]) # + self.Area_dict[Area_name].ORIGIN_POINT[2]]
                            ]
                            # break
                        else:
                            continue
        
        else:
            for x in range(self.Area_dict[Area_name].COL, 1, -1):
                for y in range(self.Area_dict[Area_name].ROW, 1, -1):
                    if len(self.Area_dict[Area_name].grid[x][y]) == 0:
                        iter += 1
                        if iter >= priority:
                            # return[x,y]
                            return [
                                x + self.Area_dict[Area_name].ORIGIN[0],
                                y + self.Area_dict[Area_name].ORIGIN[1],
                                len(self.Area_dict[Area_name].grid[x][y]) + self.Area_dict[Area_name].ORIGIN[2]]
                            # break
                        else:
                            continue
        
       
        return False



    def waiting_Gantry_get_ready(self):
        while (not self.Modbus_inst.mission_enabled) or (self.Modbus_inst.mission_running):
            print("waiting for the Gantry is ready...")
            time.sleep(0.5)
        print("PLC READY !")


    
    def move_item(self, area_from, loc_from, area_to, loc_to):
        global_loc_from = [a+b for a,b in zip(loc_from,area_from.ORIGIN_POINT)]
        global_loc_to = [a+b for a,b in zip(loc_to,area_to.ORIGIN_POINT)]

        self.waiting_Gantry_get_ready()

        set_list = [1] + global_loc_from + [1] + [0] + global_loc_to + [2] + [0]
        self.Modbus_inst.mission_enabled = False
        self.Modbus_inst.mission_running = True
        
        self.Modbus_inst.write(address=0, set_list=set_list)

        lot = area_from.grid[loc_from[0]][loc_from[1]].pop()
        self.Area_dict['Gantry'].grid[0][0].append(lot) # 변경 여부 검토 필요
        
        
            
        while True:
            # try:
            #     res = self.Modbus_inst.read(address=0, nb = 20, reshape= 20) # [0]
                
            #     recieved = True
            # except IndexError or TypeError:
            #     recieved = False
            #     continue

            # finally:
            #     if recieved and type(res)==type([]) and res[11:13] == [0,1]:
            #         lot = self.Area_dict['Gantry'].grid[0][0].pop()
            #         area_to.grid[loc_to[0]][loc_to[1]].append(lot)
            #         print(f"{lot} : {area_from.AREA_NAME}{loc_from} -> {area_to.AREA_NAME}{loc_to}")
            #         break
            
            if not self.Modbus_inst.mission_running and self.Modbus_inst.mission_enabled:
                lot = self.Area_dict['Gantry'].grid[0][0].pop()
                area_to.grid[loc_to[0]][loc_to[1]].append(lot)
                print(f"{lot} : {area_from.AREA_NAME}{loc_from} -> {area_to.AREA_NAME}{loc_to}")
                break

    # def pick_item(self, lot, Area_name, ):
    #     set_list = [1] + loc + [1] + Out.ORIGIN_POINT + [2]
    #     self.Modbus_inst.write(address=0, set_list=set_list)

    

    


    
    

