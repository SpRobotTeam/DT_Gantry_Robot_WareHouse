import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# from Info_mng import Base_info
from WCS.Info_mng import Base_info
import random as rand
# from MW.MW import m

class GantryWCS (Base_info):
    def __init__(self, op_mode = None):
        Base_info.__init__(self, op_mode=op_mode)
        # self.base_info = Base_info()
        
        
    # def __init__(self, saved_file):
    #     self.base_info = info_manager.__init__(saved_file)
    #     self.area_manger = base_info.area_manager


if __name__ == '__main__':
    # wcs_DT = GantryWCS()
    # # wcs_DT.__init__()
    # wcs_DT.add_default_WH()

    # box_amount = 16

    # for _ in range(box_amount):
    #     wcs_DT.Inbound()

    # _ = 0
    # while _ < box_amount:
    #     product = rand.choice(list(wcs_DT.product_I_dict.keys()))
    #     if 'WH_name' in wcs_DT.product_I_dict[product].keys():
    #         wcs_DT.Outbound(product)
    #         _ += 1
        

    # print("test_fin")
    print(
        "이 프로그램은 직접 실행 할 수 없습니다. ",
        "이 모듈을 다른 프로그램에서 불러와서 사용하세요."
          )

    

        
    # DT_WH = {
    #     'name' : 'DT_WH',
        
    # }
    # wcs_DT.base_info.add_WH(DT_WH)
    # wcs_DT.base_info.WH_dict['DT_WH'].add_zone()



    


    