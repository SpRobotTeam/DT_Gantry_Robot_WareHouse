import Zone_mng 
from MW.Product_mng import container_manager, product_manager
import numpy as np

class base_info (product_manager, container_manager):
    Zone_list = []
    def __init__(self):
        # self.Area_list.append(area_manager.area_manager())
        # # self.Box.append(container.container())
        # self.Box.append(product_manager.container())
        # self.product.append(product_manager.product())

        container_manager.__init__()
        product_manager.__init__()        

        # self.container_manager.add_container(container_name='default')
        # product_manager.add_product()

        self.Zone_01 = Zone_mng.zone_manager(container=container_manager.container_dict['default'])
        self.Zone_list.append('Zone_01')
        
        # self.Area_01 = Area_mng.area_manager(
        #     container_type=container_manager.container_dict['defalut']
        #     )

      
    # def __init__(self, saved_file):
    #     pass

    # def __init__(self, area_name, product_name, ):
    #     pass
        
    def find_loc(target)->list[int, int, int]:
        try:
            return product_manager.product_I_dict[target]['bin_location']
        except KeyError:
            return False
        
    def Inbound(self, lot, product_name, DOM, manufactor='', Area_name='', Zone_name='', WH_name='', ):
        lot_head = lot[:10]
        
        if lot_head not in product_manager.product_templet_dict.keys():
            register_new_product_templet = \
            input(f"입력하신 제품 종 '{product_name}'은(는) 등록되어 있지 않습니다.\n"+ 
                  "새로 등록하시겠습니까? 신규 등록하지 않는 경우 기본값으로 등록됩니다.\n"+ 
                  ">> ")
            if register_new_product_templet:
                input_dict = {}
                print("아래의 값을 입력해주세요. 빈칸으로 비울 시(값을 입력하지 않고 엔터) \n"+ 
                        " 초기값이 적용됩니다.")
                for i,j in [['flameable',         "화재 위험성 : 'high' or 'low' \n"+ 
                                                  ">> "],

                            ['perishable',        "화학적 변성 위험성 : 'high' or 'low' \n"+ 
                                                  ">> "],

                            ['container',         "상품 포장 규격 이름 : '이름' \n"+ 
                                                  ">> "],

                            ['container',         "상품 포장 규격 크기 : [x,y,z](mm) \n"+ 
                                                  ">> "],

                            ['combination_indices',"상품 세부 분류 (띄어쓰기 없이 ','로 분류. 단일 분류시 'x'): [0,... ] \n"+ 
                                                  ">> "],

                            ['weight',            "무개 (kg) : nn  \n"+ 
                                                  ">> "],

                            ['inbound_frequency', "입고 빈도 : 'high' or 'low' \n"+ 
                                                  ">> "],

                            ['outbound_frequency',"출고 빈도 : 'high' or 'low' \n"+ 
                                                  ">> "],
                    ]:
                    input_dict[i] = input(j)

                    product_manager.add_product_templet(lot_head, # =lot_head, 
                                                        product_name, # =product_name,
                                                        # flameable = flameable,
                                                        # perishable = perishable,
                                                        # container = container,
                                                        # combination_indices = combination_indices,
                                                        # weight = weight,
                                                        # inbound_frequency = inbound_frequency,
                                                        # outbound_frequency = outbound_frequency,
                                                        input_dict
                                                        )
        
        self.load_templet()

        # if not WH_name:
        #     pass
        if not Zone_name:
            Zone_name = self.Zone_list[-1]
        if not Area_name:
            Area_name = self.Area_list[-1]
            pass

        loc = self.pr
        self.Zone_01.inbound(loc=loc)

        self.add_product(product_name=product_name, 
                         DOM = DOM,
                         manufactor=manufactor, 
                         bin_location= loc,
                         Zone_name = Zone_name,
                         Area_name = Area_name
                         )
        


    def Outbound(self, name):  #lot_head/name
        loc = self.find_loc(name)
        if loc:
            self.Zone_01.outbound(loc)