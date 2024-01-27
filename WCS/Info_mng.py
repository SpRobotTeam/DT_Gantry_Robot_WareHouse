from WH_mng import wh_manager
from MW.Product_mng import container_manager, product_manager
# import numpy as np
import datetime as dt

class Base_info (product_manager, container_manager, wh_manager):
    def __init__(self):
        self.WH_dict = {}

        container_manager.__init__(self)
        
        product_manager.__init__(self, container_manager)        

      
    # def __init__(self, saved_file):
    #     pass


    # def __init__(self, area_name, product_name, ):
    #     pass
        

    def add_default_WH(self):
        self.WH_01 = wh_manager
        self.WH_01.__init__(self)
        self.WH_dict['WH_01'] = self.WH_01
        self.WH_01.Zone_dict = self.add_default_zone(**self.container_dict['default'])
        


    def add_WH(self,WH_properties):
        self.WH_dict[WH_properties['name']] = globals (
                                                        f"{WH_properties['name']}", 
                                                        wh_manager(WH_properties))


    # def find_loc(self, target)->list[int, int, int]:
    #     try:
    #         return product_manager.product_I_dict[target]['bin_location']
    #     except KeyError:
    #         return False
        


    def Inbound(
            self, 
            # lot_head = '0000-DFT-0000', 
            product_name = 'default', 
            DOM = None, 
            manufactor='', 
            WH_name='', 
            Zone_name='', 
            Area_name='', 
            manual_loc=[]
            ):
        
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
            if len(register_new_product_templet) ==0 or not register_new_product_templet[0].lower == 'y':
                
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
            Zone_name = list(self.Zone_dict.keys())[-1]
        if not Area_name:
            # Area_name = list(self.Area_dict.keys())[-1]
            Area_name = 'Area_01'
            
        destination_WH   = self.WH_dict[WH_name]
        destination_zone = self.WH_dict[WH_name].Zone_dict[Zone_name]
        destination_area = self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict[Area_name]
        In_area          = self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict['In']

        present_product_amount = len([i for i in destination_area.inventory.keys() if product_name == i])
        # lot = f"{self.product_templet_dict[product_name]['lot_head']}-{DOM}-{present_product_amount}"

        if manual_loc:
            loc = manual_loc

        else:
            if present_product_amount%destination_area.height:
                priority = 2
            else:
                priority = 1
            
            loc = self.optimal_pos_find(area_name=Area_name, 
                                outbound_freq = self.product_templet_dict[product_name]['outbound_frequency'], 
                                priority=priority)

        # self.Zone_01.inbound(loc=loc)
            
        self.move_item(area_from=In_area, 
                       loc_from=In_area.origin_point, 
                       area_to=destination_area, 
                       loc_to = loc) # product_name/lot_head
                                
        
        # loc = self.WH_dict[WH_name].Zone_dict[Zone_name].pos_find(
        #         area_name=Area_name,
        #         priority = priority
        #     )


        self.resister_item(
                         I_id=present_product_amount,
                         product_name=product_name, 
                         DOM = DOM,
                         manufactor=manufactor,
                         WH_name   = WH_name,
                         Zone_name = Zone_name,
                         Area_name = Area_name,
                        #  bin_location= f"{WH_name}_{Zone_name}_{Area_name}_{loc[0]:03d}{loc[1]:03d}{loc[2]:03d}",
                        bin_location=loc
                         )
        


    def Outbound(self, lot):  #lot_head/name
        # loc = self.find_loc(name)
        I_dict = self.product_I_dict[lot]
        WH_name = I_dict['WH_name']
        Zone_name = I_dict['Zone_name']
        Area_name = I_dict['Area_name']
        loc = I_dict['bin_location']

        if loc:
            if (loc[-1] == 
                self.WH_dict[WH_name].
                Zone_dict[Zone_name].
                Area_dict[Area_name].
                grid[loc[0]][loc[1]].index(lot)
                ):
                self.Zone_01.outbound(loc)

                Out_area= self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict['Out']

                self.move_item(area_from=self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict[Area_name],
                                loc_from=loc, 
                                area_to= self.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict['Out'],
                                loc_to = Out_area.origin_point) # product_name/lot_head



    def sort(self,):
        pass
    

    def rearrange_Area(self,):
        pass

    def sort_item(self):
        pass


    
    # def find_oldest_item(self, area_name, product_name, ):
    #     pass





    

    

    
    def read_stock_state(self)->list:
        pass


    def write_stock_state(self, target, state):
        pass