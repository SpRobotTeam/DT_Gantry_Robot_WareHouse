import WCS.area_manager as area_manager
import MW.product_manager as product_manager
import numpy as np

class base_info ():
    # Area_list = Container_list = Product_list = []

    def __init__(self):
        # self.Area_list.append(area_manager.area_manager())
        # # self.Box.append(container.container())
        # self.Box.append(product_manager.container())
        # self.product.append(product_manager.product())
        
        self.product_01 = product_manager.product()

        self.In      = area_manager.area_manager(area_name="In",     origin_point=[0,0],  row_block=15, col_block=3,  height_block=8, grid_type='r')
        self.Temp    = area_manager.area_manager(area_name="temp",   origin_point=[0,30], row_block=1 , col_block=3,  height_block=8, grid_type='r')
        self.Out     = area_manager.area_manager(area_name="Out",    origin_point=[0,31], row_block=15, col_block=3,  height_block=8, grid_type='r')
        self.Area_01 = area_manager.area_manager(area_name="Area_01",origin_point=[3,0],  row_block=31, col_block=34, height_block=8, grid_type='r')
        



    def __init__(self, saved_file):
        pass

    def __init__(self, area_name, product_name, ):
        pass
        
