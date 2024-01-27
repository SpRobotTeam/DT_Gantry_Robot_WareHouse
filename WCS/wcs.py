from Info_mng import Base_info
# from MW.MW import m

class GantryWCS (Base_info):
    def __init__(self):
        Base_info.__init__()
        # self.base_info = Base_info()
        
        
    # def __init__(self, saved_file):
    #     self.base_info = info_manager.__init__(saved_file)
    #     self.area_manger = base_info.area_manager


if __name__ == '__main__':
    wcs_DT = GantryWCS()

    wcs_DT.add_defualt_WH()

    for iter in range(100):
        wcs_DT.Inbound()

    

        
    # DT_WH = {
    #     'name' : 'DT_WH',
        
    # }
    # wcs_DT.base_info.add_WH(DT_WH)
    # wcs_DT.base_info.WH_dict['DT_WH'].add_zone()



    


    