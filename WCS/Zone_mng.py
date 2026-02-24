from WCS.Area_mng import area_manager
import math
import MW.PLC_com as PLC_com
import time
import os

import logging
logger = logging.getLogger('main')

PORT = 502 if 'nt' in os.name else 2502

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
        self.Area_dict[Area_name] = area_manager(
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
    


    def optimal_pos_find(self, Area_name, outbound_freq, priority, origin = None, lot=None):  # origin=[0,0], #! mode('FF' or 'AO' ...) 관련 수정 필요
        '''
        구역 특성과 상품의 outbound_freq, priority에 따라 적절한 위치 탐색

        현재 First-Fit 과 유사한 방식 사용
        높이가 0인 곳 부터 찾다가 `AREA_DICT`에 설정된 높이 한계 까지 찾아감
        '''
        iter = 0
        if len(outbound_freq) == 0 or outbound_freq[0].lower() != 'l':
        # global_loc = [0,0,0]
            for z in range(0,self.Area_dict[Area_name].HEIGHT):
                for x in range(self.Area_dict[Area_name].COL):
                    for y in range(self.Area_dict[Area_name].ROW):
                        if origin and [x,y] == origin: # 같은 X,Y 좌표 회피
                            continue
                        elif len(self.Area_dict[Area_name].grid[x][y]) == z:
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
            for z in range(0,self.Area_dict[Area_name].HEIGHT):
                for x in range(self.Area_dict[Area_name].COL-1, -1, -1):
                    for y in range(self.Area_dict[Area_name].ROW-1, -1, -1):
                        if origin and [x,y] == origin: # 같은 X,Y 좌표 회피
                            continue
                        elif len(self.Area_dict[Area_name].grid[x][y]) == z:
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
        
       
        return False



    def waiting_Gantry_get_ready(self):
        while (not self.Modbus_inst.mission_enabled) or (self.Modbus_inst.mission_running):
            logger.info("waiting for the Gantry is ready...")
            time.sleep(0.5)
        logger.info("PLC READY !")


    
    def move_item(self, area_from, loc_from, area_to, loc_to, MODBUS_SIM_SKIP = None) -> list:
        global_loc_from = [a+b for a,b in zip(loc_from,area_from.ORIGIN_POINT)]
        global_loc_to = [a+b for a,b in zip(loc_to,area_to.ORIGIN_POINT)]

        HEIGHT = max(area_from.HEIGHT, area_to.HEIGHT)

        self.new_mission_finished = False
        while not self.new_mission_finished:
            if not MODBUS_SIM_SKIP :
                self.waiting_Gantry_get_ready()

                set_list = [1] + global_loc_from + [1] + global_loc_to + [2] + [0]
                self.Modbus_inst.mission_enabled = False
                self.Modbus_inst.mission_running = False

                while not self.Modbus_inst.mission_enabled: # 갠트리 작동 완료 까지 대기
                    time.sleep(0.1)

                while not (self.Modbus_inst.mission_running or self.new_mission_finished): # 갠트리 명령 대기 중
                    if self.Modbus_inst.modbus_data[:10] == set_list:
                        if self.Modbus_inst.modbus_data[13]:
                            self.new_mission_finished = True
                            
                            lot = area_from.grid[loc_from[0]][loc_from[1]].pop()
                            # self.Area_dict['Gantry'].grid[0][0].append(lot)
                            # lot = self.Area_dict['Gantry'].grid[0][0].pop()
                            area_to.grid[loc_to[0]][loc_to[1]].append(lot)
                            logger.info(f"{lot} : {area_from.AREA_NAME}{loc_from} -> {area_to.AREA_NAME}{loc_to}")
                            self.Modbus_inst.write(0,set_list=[0]*9)
                            
                    else:
                        self.Modbus_inst.write(address=0, set_list=set_list)
                    time.sleep(0.5)
                    # self.Modbus_inst.plc_check()

                if not self.new_mission_finished:
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
                        #         logger.info(f"{lot} : {area_from.AREA_NAME}{loc_from} -> {area_to.AREA_NAME}{loc_to}")
                        #         break
                        try:
                            if (self.Modbus_inst.modbus_data[:10] == set_list and
                                not self.Modbus_inst.mission_running):

                                self.new_mission_finished = True
                                self.Modbus_inst.write(0,set_list=[0]*9)
                                time.sleep(0.5)
                        except IndexError:
                            pass

                        if (self.Modbus_inst.mission_enabled and 
                            self.new_mission_finished and 
                            not self.Modbus_inst.mission_running):

                            lot = self.Area_dict['Gantry'].grid[0][0].pop()
                            area_to.grid[loc_to[0]][loc_to[1]].append(lot)
                            logger.info(f"{lot} : {area_from.AREA_NAME}{loc_from} -> {area_to.AREA_NAME}{loc_to}")
                            break
                    # else:
                    #     pass

            elif MODBUS_SIM_SKIP:
                lot = area_from.grid[loc_from[0]][loc_from[1]].pop()
                self.Area_dict['Gantry'].grid[0][0].append(lot) # 변경 여부 검토 필요

                lot = self.Area_dict['Gantry'].grid[0][0].pop()
                area_to.grid[loc_to[0]][loc_to[1]].append(lot)
                logger.info(f"{lot} : {area_from.AREA_NAME}{loc_from} -> {area_to.AREA_NAME}{loc_to}")
                self.new_mission_finished = True
        
        # 리스트 [XY 평면 이동 거리, Z축 이동 거리] 반환
        
        dist = [loc_to-loc_from for loc_from,loc_to in zip(global_loc_from,global_loc_to)]
        return_val =  [math.sqrt(pow(dist[0],2)+pow(dist[1],2)),
                        abs(HEIGHT-global_loc_from[-1])+abs(HEIGHT-global_loc_to[-1])]
        
        return return_val
