# import sys, os
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from WCS.Area_mng import area_manager
import math
import numpy as np
import MW.PLC_com as PLC_com


class zone_manager():
    def __init__(self, 
                 container
                 ):
        self.container = container
        self.Modbus_inst = PLC_com.plc_com()
        self.Area_dict = {}

    
    def add_area(self, area_properties_dict):
        # self.exec()
        
        area_name = area_properties_dict['area_name']
        self.Area_dict[area_name] = \
            locals()[area_name] = \
                area_manager(
                    area_name=area_name,
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

        self.col_total    = area_length//self.container['length'] # 34
        self.row_total    = area_width //self.container['width']  # 31        
        self.heigth_total = area_height//self.container['height'] # 8
        
        Gantry = area_manager(   
                                    # Gantry, 
                                    # area_manager,
                                    area_name="Gantry",   
                                    origin_point=[0,math.ceil(self.row_total/2),0], 
                                    col_block=1,  
                                    row_block=1 , 
                                    height_block=self.heigth_total, 
                                    grid_type='r'
                                    )
        self.Area_dict['Gantry'] = Gantry

        In      = area_manager(
                                    # In,
                                    # area_manager,
                                    area_name="In",     
                                    origin_point=[0,self.row_total,0],  
                                    col_block=1,  
                                    row_block=1, 
                                    height_block=self.heigth_total, 
                                    grid_type='r'
                                    )
        self.Area_dict['In'] = In

        Out     = area_manager(
                                    # Out,
                                    # area_manager,
                                    area_name="Out",    
                                    origin_point=[0,0,0], 
                                    col_block=1,  
                                    row_block=1, 
                                    height_block=self.heigth_total, 
                                    grid_type='r'
                                    )
        self.Area_dict['Out'] = Out

        Area_01 = area_manager(
                                    # Area_01,
                                    # area_manager,
                                    area_name="Area_01",
                                    origin_point=[1,0,0],  
                                    col_block=self.col_total-1, 
                                    row_block=self.row_total, 
                                    height_block=self.heigth_total, 
                                    grid_type='r'
                                    )
        self.Area_dict['Area_01'] = Area_01

        return self # self.Area_dict
    


    def optimal_pos_find(self, lot, area_name, outbound_freq, priority):  # origin=[0,0],
        '''
        구역 특성과 상품의 outbound_freq, priority에 따라 적절한 위치 탐색

        현재 First-Fit 과 유사한 방식 사용
        '''
        iter = 0
        if outbound_freq[0].lower() == 'h':
        # global_loc = [0,0,0]
            for x in range(self.Area_dict[area_name].col):
                for y in range(self.Area_dict[area_name].row):
                    if len(self.Area_dict[area_name].grid[x][y]) == 0:
                        iter += 1
                        if iter == priority:
                            # return[x,y]
                            return [
                                x ,# + self.Area_dict[area_name].origin_point[0],
                                y ,# + self.Area_dict[area_name].origin_point[1],
                                len(self.Area_dict[area_name].grid[x][y]) # + self.Area_dict[area_name].origin_point[2]]
                            ]
                            # break
                        else:
                            continue
        
        else:
            for x in range(self.Area_dict[area_name], 1, -1).col:
                for y in range(self.Area_dict[area_name], 1, -1).row:
                    if len(self.Area_dict[area_name].grid[x][y]) == 0:
                        iter += 1
                        if iter == priority:
                            # return[x,y]
                            return [
                                x + self.Area_dict[area_name].origin[0],
                                y + self.Area_dict[area_name].origin[1],
                                len(self.Area_dict[area_name].grid[x][y]) + self.Area_dict[area_name].origin[2]]
                            # break
                        else:
                            continue
        
       
        return False

    def move_item(self, area_from, loc_from, area_to, loc_to):
        global_loc_from = [a+b for a,b in zip(loc_from,area_from.origin_point)]
        global_loc_to = [a+b for a,b in zip(loc_to,area_to.origin_point)]

        set_list = [1] + global_loc_from + [1] + [0] + global_loc_to + [2] + [0]
        self.Modbus_inst.write(address=0, set_list=set_list)

        lot = area_from.grid[loc_from[0]][loc_from[1]].pop()
        self.Area_dict['Gantry'].grid[0][0].append(lot) # 변경 여부 검토 필요
        recieved = False
        while True:
            try:
                res = self.Modbus_inst.read(address=0, nb = 20, reshape= 20)[0]
                recieved = True
            except IndexError or TypeError:
                recieved = False
                # continue

            finally:
                if recieved and type(res)==type([]) and res[11] == 1:
                        break
            

        recieved = False
        while True:
            try:
                res = self.Modbus_inst.read(address=0, nb = 20, reshape= 20)[0]
                recieved = True
            except IndexError or TypeError:
                recieved = False
                continue

            finally:
                if recieved and type(res)==type([]) and res[11:13] == [0,1]:
                    lot = self.Area_dict['Gantry'].grid[0][0].pop()
                    area_to.grid[loc_to[0]][loc_to[1]].append(lot)
                    break

    # def pick_item(self, lot, area_name, ):
    #     set_list = [1] + loc + [1] + Out.origin_point + [2]
    #     self.Modbus_inst.write(address=0, set_list=set_list)

    

    


    
    

