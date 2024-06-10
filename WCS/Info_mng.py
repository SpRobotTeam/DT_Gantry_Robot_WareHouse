# import sys, os
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from WCS.WH_mng import wh_manager
from WCS.Zone_mng import zone_manager
from WCS.Area_mng import area_manager
from MW.Product_mng import container_manager, product_manager
# import numpy as np
import datetime as dt
import math

from ERROR.error import NotEnoughSpaceError, ProductNotExistError


MODE = "FF"

class Base_info (product_manager, container_manager, wh_manager):
    def __init__(self, op_mode = None):
        self.op_mode = op_mode
        if op_mode in ['no_sim']:   
            self.sim_skip = True
        else:
            self.sim_skip = False
        # if op_mode != None and op_mode[0] in ['s', ]:
        #     self.sim_skip = True
            
        self.WH_dict = {}
        container_manager.__init__(self)
        
        product_manager.__init__(self, container_manager)        

      
    # def __init__(self, saved_file):
    #     pass


    # def __init__(self, area_name, product_name, ):
    #     pass
        

    def add_default_WH(self):
        # self.WH_01 = wh_manager
        # self.WH_01.__init__(self.WH_01)

        self.WH_01 = wh_manager(
            {
                'WH_name':'WH_01'
                }
        )
        self.WH_dict['WH_01'] = self.WH_01
        # self.WH_01.Zone_dict = 
        wh_manager.add_default_zone(self.WH_01, {
                'Zone_name' : 'Zone_01',
                'container' : self.container_dict['default']
                }
            )
        


    def add_WH(self,WH_properties):
        self.WH_dict[WH_properties['WH_name']] = \
            locals()[f"{WH_properties['WH_name']}"] = \
                wh_manager(WH_properties)
        # self.WH_dict[WH_properties['name']] =  locals()[f"{WH_properties['name']}"]
                
                                                        


    # def find_loc(self, target)->list[int, int, int]:
    #     try:
    #         return product_manager.product_I_dict[target]['bin_location']
    #     except KeyError:
    #         return False
        


    def Inbound(
            self, 
            # lot_head = '0000-DFT-0000', 
            product_name = 'default', 
            DOM = '', 
            manufactor='', 
            WH_name='', 
            Zone_name='', 
            Area_name='', 
            reserved_time=None,
            manual_loc=[],
            testing_mode = None,
            )->list:
        '''
        입고 명령

        출력 : [`moved_distance`,`lot`]
        '''
        sum_distance = [0,0]

        if not DOM:
            date = dt.datetime.now()
            DOM = f"{date.year:02d}{date.month:02d}{date.day:02d}"
        if not manufactor:
            manufactor = 'SPSystems'
        if (product_name not in self.product_templet_dict.keys()): # product_name/lot_head
            register_new_product_templet = input(
                f"입력하신 제품 종 '{product_name}'은(는) 등록되어 있지 않습니다.\n"+ 
                  "새로 등록하시겠습니까? 신규 등록하지 않는 경우 기본값으로 등록됩니다.\n"+ 
                  "[yes / [no]]>> ")
            if len(register_new_product_templet) ==0 or not register_new_product_templet.lower()[0] == 'y':
                
                product_name = 'default'
            else:
                self.add_product_templet(
                    # lot_head=lot_head, 
                    product_name=product_name
                    )
                # lot_head = product_manager.product_templet_dict['default']['lot_head']
        # self.load_templet(lot_head)                
        self.product_templet = self.product_templet_dict[product_name]
        if not WH_name:
            WH_name = list(self.WH_dict.keys())[-1]
        if not Zone_name:
            Zone_name = list(self.WH_dict[WH_name].Zone_dict.keys())[-1]
        if not Area_name:
            Area_name = list(self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict.keys())[-1]
            # Area_name = 'Area_01'


        destination_WH   = self.WH_dict[WH_name]
        destination_zone = self.WH_dict[WH_name].Zone_dict[Zone_name]
        destination_area = self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict[Area_name]
        In_area          = self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict['In']

        area_total_product_amount = len([i for i in destination_area.inventory.keys() 
                                      if 'loc' in destination_area.inventory[i].keys()])

        present_product_amount = len([i for i in destination_area.inventory.keys() 
                                      if self.product_templet_dict[product_name]['lot_head'] in i])
        
        registered_product_amount = len([i for i in self.product_I_dict.keys() 
                                      if self.product_templet_dict[product_name]['lot_head'] in i])
        
        if area_total_product_amount >= destination_area.INVENTORY_CRITICAL_LIMIT: # 물건을 하나씩 집는 동안은 해결 불능
            print("최종 적재 한계에 도달 하였습니다. \n입고 작업 및 정렬 작업을 진행할 수 없습니다.")
            raise NotEnoughSpaceError
        
        # elif area_total_product_amount >= destination_area.INVENTORY_LIMIT: # 다른 전략 필요
        #     print("적재 한계에 도달 하였습니다. \n정렬 작업을 진행할 수 없습니다.")
        #     raise NotEnoughSpaceError
        
        lot = f"{self.product_templet_dict[product_name]['lot_head']}-{DOM}-{registered_product_amount+1:04d}"
        

        In_area.grid[0][0].append(lot) # 박스 추가 : 변경 여부 검토 필요


        if manual_loc:
            loc = manual_loc

        else:
            # 자동 최적화
            if MODE == "AO":
                if (present_product_amount == 0                                               #AO
                    or (present_product_amount+1)%destination_area.HEIGHT):                   #AO
                    priority = 2                                                              #AO
                else:                                                                         #AO
                    priority = 1                                                              #AO
            
            # first_fit
            if MODE == "FF":                                                                  #FF
                priority = 1                                                                  #FF
            
            loc = zone_manager.optimal_pos_find(
                                self=destination_zone,
                                lot=lot,
                                Area_name=Area_name, 
                                outbound_freq = self.product_templet_dict[product_name]
                                                ['outbound_frequency'], 
                                priority=priority
                                )

        # self.Zone_01.inbound(loc=loc)
        
        # height = len(In_area.grid[loc[0]][loc[1]])-1

        moved_distance = zone_manager.move_item(
                                    self=destination_zone,
                                    area_from=In_area, 
                                    loc_from=[0,0,0],
                                    # loc_from=[0, 0, [a+b for a,b in 
                                    #                  zip([0,0,height],In_area.origin_point)].index(lot)],
                                    area_to=destination_area, 
                                    loc_to = loc,
                                    MODBUS_SIM_SKIP = self.sim_skip
                                    ) 
                                
        sum_distance = [m+s for m,s in zip(moved_distance,sum_distance)]
        
        # loc = self.WH_dict[WH_name].Zone_dict[Zone_name].pos_find(
        #         area_name=Area_name,
        #         priority = priority
        #     )


        self.register_item(
                         I_id=registered_product_amount,
                         product_name=product_name, 
                         DOM = DOM,
                         manufactor=manufactor,
                         WH_name   = WH_name,
                         Zone_name = Zone_name,
                         Area_name = Area_name,
                        #  bin_location= f"{WH_name}_{Zone_name}_{Area_name}_{loc[0]:03d}{loc[1]:03d}{loc[2]:03d}",
                        bin_location=loc
                         )
        
        self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict[Area_name].inventory[lot] = {
                        'loc' : loc
                    }
        # 자동 최적화
        if MODE == "AO":
            if priority == 1:                                     #AO
                moved_distance = self.sort_item( # 정렬           #AO
                                WH_name=WH_name,                  #AO
                                Zone_name=Zone_name,              #AO
                                Area_name=Area_name,              #AO
                                lot=lot,                          #AO
                                loc=[loc[0],loc[1],loc[2]+1],     #AO
                                offset=2                          #AO
                                )                                 #AO

                sum_distance = [m+s for m,s in zip(moved_distance,sum_distance)]

        print(f"{lot} : {Area_name}{loc}에 입고 완료",
              f"{'- '+destination_area.grid[loc[0]][loc[1]][-1]+'~'+lot}"
              + f"{' 정렬 완료됨'if priority == 1 else ''}" if MODE == "AO" else ''  #AO
              )
        
        # if testing_mode:
        #     return sum_distance
        # else:
        #     return None    
        return [sum_distance, lot]

    def Outbound(self, 
                 lot:str=None, 
                 product_name:str=None, 
                #  loc:list=None, 
                 reserved_time=None, 
                 testing_mode = None,
                 )->list:  #lot_head/name
        '''
        출고 명령

        출력 : [`moved_distance`,`lot`]
        '''
        # loc = self.find_loc(name)
        if not lot:
            if product_name:
                product_I_dict_sorted = dict(sorted(self.product_I_dict.items()))


                for i in product_I_dict_sorted.keys():
                    if (
                        product_I_dict_sorted[i]['product_name'] == product_name and
                        'bin_location' in list(product_I_dict_sorted[i].keys())
                        ):
                        lot = i
                        break

            # elif loc:

        if not lot:
            raise ProductNotExistError
            # return None

        sum_distance = [0,0]

        print(f"출고 대상 : {lot}")
        I_dict      = self.product_I_dict[lot]
        WH_name     = I_dict['WH_name']
        Zone_name   = I_dict['Zone_name']
        Area_name   = I_dict['Area_name']
        loc         = I_dict['bin_location']
        
        deposition_WH   = self.WH_dict[WH_name]
        deposition_zone = self.WH_dict[WH_name].Zone_dict[Zone_name]
        deposition_area = self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict[Area_name]
        
        previous_height = len(deposition_area.grid[loc[0]][loc[1]])

        Out_area        = self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict['Out']

        if loc:
            
            while loc[-1]+1 != len(deposition_area.grid[loc[0]][loc[1]]):

                top_lot = (deposition_area.grid[loc[0]][loc[1]][-1])
                product_name = self.product_I_dict[top_lot]['product_name']
                
                # 자동 최적화
                if MODE == "AO":
                    priority = 2                    #AO
                # first_fit
                elif MODE == "FF":
                    priority = 1                    #FF

                deposition_loc = zone_manager.optimal_pos_find(
                                    self = deposition_zone,
                                    Area_name = Area_name,
                                    lot = top_lot,
                                    outbound_freq = self.product_templet_dict[product_name]['outbound_frequency'],
                                    priority = priority,
                                    origin=loc[:-1]    
                                    )
                
                moved_distance = zone_manager.move_item( # 상단 상품 이동
                    self = deposition_zone,
                    area_from = deposition_area,
                    loc_from = [loc[0],loc[1],len(deposition_area.grid[loc[0]][loc[1]])-1],
                    area_to = deposition_area,
                    loc_to = deposition_loc,
                    MODBUS_SIM_SKIP = self.sim_skip
                    )
                
                sum_distance = [m+s for m,s in zip(moved_distance,sum_distance)]

                self.product_I_dict[top_lot]['bin_location'] = deposition_area.inventory[top_lot]['loc'] = deposition_loc
                
                
            # height = len(Out_area.grid[0][0])-1

            moved_distance = zone_manager.move_item( # 목표 상품 이동
                self = deposition_zone,
                area_from = deposition_area,
                loc_from = loc,
                area_to = Out_area,
                # loc_to = [0, 0, [a+b for a,b in 
                #         zip([0,0,height],Out_area.origin_point)]]
                loc_to = [0,0,0],
                MODBUS_SIM_SKIP = self.sim_skip
            )

            sum_distance = [m+s for m,s in zip(moved_distance,sum_distance)]

            rearrange_offset = len(list(deposition_area.inventory.keys()))\
                                -list(deposition_area.inventory.keys()).index(lot) 
            
            deposition_area.inventory.pop(lot)
            for k in ['WH_name','Zone_name','Area_name','bin_location']:
                self.product_I_dict[lot].pop(k)
            
            # 자동 최적화
            if MODE == "AO":
                if previous_height > 1:                   #AO
                    moved_distance = self.sort_item(      #AO  # 재 정렬 
                        WH_name = WH_name,                #AO
                        Zone_name = Zone_name,            #AO
                        Area_name = Area_name,            #AO
                        lot = lot,                        #AO
                        loc = [loc[0],loc[1],loc[-1]],    #AO
                        height = previous_height-1,       #AO
                        offset =  rearrange_offset        #AO
                    )                                     #AO
                sum_distance = [m+s for m,s in zip(moved_distance,sum_distance)]

        if Out_area.grid[0][0]:
            Out_area.grid[0][0].pop()

        print(f"{lot} 출고 완료",
              f"")
        # if testing_mode == 1:
        #     return sum_distance 
        # else:
        #     return None 
        return [sum_distance, lot]


    def sort_item(self, WH_name, Zone_name, Area_name, lot, loc, height = None, offset = 1):
        '''
        Area_manager.optimal_pos_find()에 따라 펼쳐놓은 박스를 
        높이 한계 (height)까지 한 줄로 쌓아올려 정리하는 함수

        현재 First-Fit 과 유사한 알고리즘 사용 중
        '''
        destination_WH   = self.WH_dict[WH_name]
        destination_zone = self.WH_dict[WH_name].Zone_dict[Zone_name]
        destination_area = self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict[Area_name]

        if not height:
            height = destination_area.HEIGHT
        if not offset:
            offset = 1

        base_level = loc[-1] # len(destination_area.grid[loc[0]][loc[1]])

        sum_distance = [0,0]

        for z in range(base_level, height):
            deposition_lot = list(destination_area.inventory.keys())[base_level-z-offset]
            # loc[-1] += 1
            # deposition_loc = destination_area.inventory[deposition_lot]['loc']
            deposition_loc = self.product_I_dict[deposition_lot]['bin_location']
            
            # destination_loc = [a+b for a,b in zip([0,0,offset], loc)]
            # destination_loc = [loc[0], loc[1], len(destination_area.grid[loc[0]][loc[1]])]
            destination_loc = [loc[0], loc[1], z]

           
            while True:
                
                if deposition_lot[:11] == lot [:11]:
                    
                    # upper_loc = deposition_loc[:-1]+[deposition_loc[-1]+1]
                    upper_item_list :list = destination_area.grid[deposition_loc[0]][deposition_loc[1]][deposition_loc[-1]+1:]
                    if len(upper_item_list):
                        upper_item_list.reverse()
                        destination_loc_base = zone_manager.optimal_pos_find(
                            self = destination_zone,
                            Area_name = Area_name,
                            outbound_freq = 'h',
                            priority = 2,
                            lot = upper_item_list[0],
                            origin=deposition_loc[:-1] 
                                )
                    for i in range(len(upper_item_list)):
                        temporal_destination_loc = destination_loc_base[:-1]+[destination_loc_base[-1]+i]
                        
                        moved_distance = zone_manager.move_item(
                            self = destination_zone,
                            area_from = destination_area,  
                            loc_from = destination_area.inventory[upper_item_list[i]],
                            area_to = destination_area,
                            loc_to = temporal_destination_loc,
                            MODBUS_SIM_SKIP = self.sim_skip
                            )

                        sum_distance = [m+s for m,s in zip(moved_distance,sum_distance)]
                        
                        self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict[Area_name].inventory[upper_item_list[i]]['loc'] \
                        = self.product_I_dict[upper_item_list[i]]['bin_location'] \
                        = temporal_destination_loc
                        
                        
                    moved_distance = zone_manager.move_item(
                        self = destination_zone,
                        area_from = destination_area,  
                        loc_from = deposition_loc,
                        area_to = destination_area,
                        loc_to = destination_loc,
                        MODBUS_SIM_SKIP = self.sim_skip
                        )
                    
                    sum_distance = [m+s for m,s in zip(moved_distance,sum_distance)]
                    
                    self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict[Area_name].inventory[deposition_lot]['loc'] \
                    = self.product_I_dict[deposition_lot]['bin_location'] \
                    = destination_loc
                                
                    # destination_area.inventory[destination_lot]['loc'] = destination_loc
                    # self.product_I_dict[deposition_lot]['bin_location'] = destination_loc

                    if len(upper_item_list):
                        upper_item_list.reverse()
                        destination_loc_base = deposition_loc
                        for i in range(len(upper_item_list)):
                            temporal_destination_loc = destination_loc_base[:-1]+[destination_loc_base[-1]+i]
                            
                            moved_distance = zone_manager.move_item(
                                self = destination_zone,
                                area_from = destination_area,  
                                loc_from = destination_area.inventory[upper_item_list[i]],
                                area_to = destination_area,
                                loc_to = temporal_destination_loc,
                                MODBUS_SIM_SKIP = self.sim_skip
                                )
                            sum_distance = [m+s for m,s in zip(moved_distance,sum_distance)]

                            self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict[Area_name].inventory[upper_item_list[i]]['loc'] \
                            = self.product_I_dict[upper_item_list[i]]['bin_location'] \
                            = temporal_destination_loc

                    break
                else:
                    offset+=1
        
        return sum_distance 


    def stack_reverse(self, WH_name, Zone_name, Area_name, offset, height=None):
        '''
        lot 번호가 area의 inventory:dict 중 offset번 째에 등록된 상품부터 차례대로 
        적정위치에 height 만큼 쌓는(FILO) 함수
        '''

        destination_WH   = self.WH_dict[WH_name]
        destination_zone = self.WH_dict[WH_name].Zone_dict[Zone_name]
        destination_area = self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict[Area_name]

        sum_distance = [0,0]

        if not height:
            height = destination_area.HEIGHT-1
        
        lot     = list(destination_area.inventory.keys())[offset]
        product_name = self.product_I_dict[lot]['product_name']
        optimal_pos  =  zone_manager.optimal_pos_find(
                    self = destination_zone,
                    # lot             = lot,
                    Area_name       = destination_area.AREA_NAME,
                    outbound_freq   = self.product_templet_dict[product_name]['outbound_frequency'],
                    priority        = 1
                    )
        
        for i in range(height):

            lot     = list(destination_area.inventory.keys())[offset+i]
            loc_from= destination_area.inventory[lot]['loc']
            
            loc_to  = [optimal_pos[0], optimal_pos[1], optimal_pos[0]+i]

            moved_distance = zone_manager.move_item(
                self        = destination_zone,
                area_from   = destination_area,
                loc_from    = loc_from,
                area_to     = destination_area,
                loc_to      = loc_to,
                MODBUS_SIM_SKIP = self.sim_skip
            )
            
            sum_distance = [m+s for m,s in zip(moved_distance,sum_distance)]

            self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict[Area_name].inventory[lot]['loc'] \
                = self.product_I_dict[lot]['bin_location'] \
                = loc_to
            
        print(f"{list(destination_area.inventory.keys())[offset]} ~ {list(destination_area.inventory.keys())[offset+height-1]}"
              +" : 역순 정렬")
        
        return sum_distance


    def rearrange_area(self, WH_name, Zone_name, Area_name, offset:list=None, HEIGHT:int=None):
        pass
        destination_WH   = self.WH_dict[WH_name]
        destination_zone = self.WH_dict[WH_name].Zone_dict[Zone_name]
        destination_area = self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict[Area_name]
                
        sum_distance = [0,0]

        if not HEIGHT:
            HEIGHT = destination_area.HEIGHT-1
        if not offset:
            offset = 0

        area_total_product_amount = len([i for i in destination_area.inventory.keys()
                                         if 'loc' in destination_area.inventory[i]])
                                          
        iteration = (area_total_product_amount-offset)//HEIGHT
        if (area_total_product_amount-offset)%HEIGHT:
            iteration += 1

        for i in range(offset, iteration):

            x = i//destination_area.ROW
            y = i%destination_area.ROW

            # for z in range (len(destination_area.grid[x][y])):
            # z = len(destination_area.grid[x][y])
            lot = destination_area.grid[x][y][-1]
            if (lot != list(destination_area.inventory.keys())[i*HEIGHT]
                or len(destination_area.grid[x][y])<HEIGHT
            ):
                moved_distance = self.stack_reverse(WH_name=WH_name, Zone_name=Zone_name, Area_name=Area_name,
                                   offset=i*HEIGHT+HEIGHT-1, height=HEIGHT)
                
                sum_distance = [m+s for m,s in zip(moved_distance,sum_distance)]
        
        return sum_distance

    

        # # lot = destination_area.grid[x][y][-1]
        # # product_name = self.product_I_dict[lot]['product_name']
        # # reversed_stack_pos  =  zone_manager.optimal_pos_find(
        # #     self            = destination_zone,
        # #     Area_name       = destination_area.AREA_NAME,
        # #     outbound_freq   = self.product_templet_dict[product_name]['outbound_frequency'],
        # #     priority        = 1)
        
        # for x in range(destination_area.COL):
        #     if x < offset[0]:
        #         continue
        #     for y in range(destination_area.ROW):
        #         if x == offset[0] and y < offset[1]:
        #             continue

        #         if (len(destination_area.grid[x][y]) < HEIGHT
        #             or (destination_area.index(destination_area.grid[x][y][-1])
                        
        #                 )):
        #             index = HEIGHT*x + y
        #             height_lim = len(destination_area.grid[x][y])

        #             for z in range(height_lim-1,0,-1):
        #                 loc = [x,y,z]

                        
                        
        #                 lot = destination_area.grid[x][y][z]

                        
                        
        #                 # mov

    
    # def find_oldest_item(self, area_name, product_name, ):
    #     pass





    

    

    
    # def read_stock_state(self)->list:
    #     pass


    # def write_stock_state(self, target, state):
    #     pass