from WCS.Area_mng import area_manager
import math
import MW.PLC_com as PLC_com
import time
import os

import logging
logger = logging.getLogger('main')

PORT = PLC_com.DEFAULT_PORT

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

        self.sim_skip = zone_properties_dict.get('sim_skip', False)
        if not self.sim_skip:
            self.Modbus_inst = PLC_com.plc_com(port = PORT)
        else:
            self.Modbus_inst = None
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
    


    def optimal_pos_find(self, Area_name, outbound_freq, priority, origin = None, lot=None):
        '''
        구역 특성과 상품의 outbound_freq, priority에 따라 적절한 위치 탐색

        높이 인덱스(_positions_by_height)를 활용한 O(1)~O(k) 탐색
        '''
        area = self.Area_dict[Area_name]
        reverse = len(outbound_freq) > 0 and outbound_freq[0].lower() == 'l'

        # 모든 위치가 가득 찬 경우
        if area._min_height >= area.HEIGHT:
            return False

        # priority==1, origin 없음: 최소 높이에서 바로 선택 (O(1)~O(k))
        if priority == 1 and not origin:
            positions = area._positions_by_height[area._min_height]
            if not positions:
                return False
            pos = max(positions) if reverse else min(positions)
            return [pos[0], pos[1], area._min_height]

        # 일반 경로: 높이 인덱스 순회
        origin_tuple = (origin[0], origin[1]) if origin else None
        iter_count = 0
        for z in range(area.HEIGHT):
            positions = area._positions_by_height[z]
            if not positions:
                continue
            sorted_positions = sorted(positions, reverse=reverse)
            for pos in sorted_positions:
                if origin_tuple and pos == origin_tuple:
                    continue
                iter_count += 1
                if iter_count >= priority:
                    return [pos[0], pos[1], z]

        return False


    def scored_pos_find(self, Area_name, freq_score, origin=None):
        '''
        빈도 기반 위치 선택 (RL/LA 모드용)

        freq_score: 0.0(출고 빈도 낮음=COLD) ~ 1.0(출고 빈도 높음=HOT)
        - HOT → 위쪽(z↑) + 출고구 가까이 (접근 비용 최소화)
        - COLD → 아래쪽(z↓) + 출고구 멀리 (장기 보관)

        비용함수: cost(x,y,z) = xy_dist[x][y] + (HEIGHT - 1 - z)
        '''
        area = self.Area_dict[Area_name]
        if area._min_height >= area.HEIGHT:
            return False

        origin_tuple = (origin[0], origin[1]) if origin else None
        hot = freq_score >= 0.5

        best_pos = None
        best_cost = float('inf') if hot else float('-inf')

        # HOT: 높은 z부터 (빠른 접근), COLD: 낮은 z부터 (장기 보관)
        z_range = range(area.HEIGHT - 1, -1, -1) if hot else range(area.HEIGHT)

        for z in z_range:
            positions = area._positions_by_height[z]
            if not positions:
                continue

            z_cost = area.HEIGHT - 1 - z

            # HOT 조기 종료: 이 z의 최소 비용(z_cost만)이 이미 best보다 크면 하위 z 불필요
            if hot and best_pos is not None and z_cost >= best_cost:
                break

            for pos in positions:
                if origin_tuple and pos == origin_tuple:
                    continue
                cost = area._xy_dist[pos[0]][pos[1]] + z_cost
                if hot:
                    if cost < best_cost:
                        best_cost = cost
                        best_pos = [pos[0], pos[1], z]
                else:
                    if cost > best_cost:
                        best_cost = cost
                        best_pos = [pos[0], pos[1], z]

        return best_pos if best_pos else False


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
                area_to.grid[loc_to[0]][loc_to[1]].append(lot)
                logger.info(f"{lot} : {area_from.AREA_NAME}{loc_from} -> {area_to.AREA_NAME}{loc_to}")
                self.new_mission_finished = True

        # 리스트 [XY 평면 이동 거리, Z축 이동 거리] 반환
        dx = global_loc_to[0] - global_loc_from[0]
        dy = global_loc_to[1] - global_loc_from[1]
        return [(dx*dx + dy*dy) ** 0.5,
                abs(HEIGHT - global_loc_from[2]) + abs(HEIGHT - global_loc_to[2])]
