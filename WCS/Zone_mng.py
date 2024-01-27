from Area_mng import area_manager
import PLC_com

class zone_manager(area_manager):
    def __init__(self, 
                 **container
                 ):
        self.container = container
        self.Modbus_inst = PLC_com.plc_com()
        self.Area_dict = {}

    
    def add_area(self, area_name, area_properties_dict):
        # self.exec()
        
        
        self.Area_dict['area_name'] = globals(
            f'{area_name}', 
            area_manager(area_name=area_name,
                        origin_point=area_properties_dict['origin'],  
                        col_block=area_properties_dict['col'], 
                        row_block=area_properties_dict['row'], 
                        height_block=area_properties_dict['heigth'], 
                        grid_type=area_properties_dict['grid_type']
                        )
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
        
        
        self.Gantry    = area_manager
        self.Gantry.__init__(   self, 
                                area_name="Gantry",   
                                origin_point=[1,0], 
                                col_block=1,  
                                row_block=1 , 
                                height_block=self.heigth_total, 
                                grid_type='r'
                                    )
        self.Area_dict['Gantry'] = self.Gantry

        self.In      = area_manager
        self.In.__init__(
                                    self,
                                    area_name="In",     
                                    origin_point=[0,self.row_total,0],  
                                    col_block=1,  
                                    row_block=1, 
                                    height_block=self.heigth_total, 
                                    grid_type='r'
                                    )
        self.Area_dict['In'] = self.In

        self.Out     = area_manager
        self.Out.__init__(
                                    self,
                                    area_name="Out",    
                                    origin_point=[0,0,0], 
                                    col_block=1,  
                                    row_block=1, 
                                    height_block=self.heigth_total, 
                                    grid_type='r'
                                    )
        self.Area_dict['Out'] = self.Out

        self.Area_01 = area_manager
        self.Area_01.__init__(
                                    self,
                                    area_name="Area_01",
                                    origin_point=[1,0,0],  
                                    col_block=self.col_total-1, 
                                    row_block=self.row_total, 
                                    height_block=self.heigth_total, 
                                    grid_type='r'
                                    )
        self.Area_dict['Area_01'] = self.Area_01

        return self.Area_dict
    
    

    def optimal_pos_find(self, area_name, outbound_freq, priority):  # origin=[0,0],
        '''
        구역 특성과 상품의 outbound_freq, priority에 따라 적절한 위치 탐색
        '''
        iter = 0
        if outbound_freq[0].lower() == 'h':
        # global_loc = [0,0,0]
            for y in range(self.Area_dict[area_name].row):
                for x in range(self.Area_dict[area_name].col):
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
        
        else:
            for y in range(self.Area_dict[area_name], 1, -1).row:
                for x in range(self.Area_dict[area_name], 1, -1).col:
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
        set_list = [1] + loc_from + [1] + [0] + loc_to + [2] + [0]
        self.Modbus_inst.write(address=0, set_list=set_list)

        global_loc_from = loc_from
        global_loc_to = loc_to

        for i in range(len(area_from.origon_point)):
            global_loc_from[i] += area_from.origin_point[i]
            global_loc_to[i] += area_to.origin_point[i]

        lot = area_from.grid[loc_from[0]][loc_from[1]].pop
        self.Gantry.grid[0][0].append(lot) 

        while True:
            res = self.Modbus_inst.read(address=0, nb = 20, reshape= 20)
            if res[11] == 1:
                break

        while True:
            res = self.Modbus_inst.read(address=0, nb = 20, reshape= 20)
            if res[11:13] == [0,1]:
                self.Gantry.grid[0][0].pop()
                area_to.grid[loc_to[0]][loc_to[1]].append(lot)
                break

    # def pick_item(self, lot, area_name, ):
    #     set_list = [1] + loc + [1] + self.Out.origin_point + [2]
    #     self.Modbus_inst.write(address=0, set_list=set_list)

    

    


    
    

