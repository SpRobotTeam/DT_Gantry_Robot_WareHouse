# import sys, os
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class container_manager():
    container_dict = {
        'default':{
            'name'      : 'default',
            'length'    : 304.8, # 300, 
            'width'     : 177.8, # 200, 
            'height'    : 133.7, # 200,
            'gap'       : 100
            },
    }

    def __init__(self):
        return self


    # def __init__(self, saved_file):
    #     pass


    def add_container(self, container_name:str): # , **kwargs):
        kwargs = {'name' : container_name}
        print("아래의 값을 입력해주세요. 빈칸으로 비울 시(값을 입력하지 않고 엔터) \n"+ 
                " [초기값]이 적용됩니다.")
        # name = input('규격 이름' + ">> ")
        for i,j in [[   'length'    , '길이 (mm) [100]\n' + ">> "], 
                    [   'width'     , '너비 (mm) [100]\n' + ">> "], 
                    [   'height'    , '높이 (mm) [100]\n' + ">> "],
                    [   'gap'       , '최대 배치 간격 (전후 좌우 동일) (mm) [100]\n' + ">> "]
        ]:
            kwargs[i] = input(j)  

        # for key, val in kwargs.items():
        #     # self.container_dict[container_name][key] = val
        #     self.container_dict[container_name][key] = val
        self.container_dict[container_name] = kwargs if kwargs else 100

    

class product_manager():

    product_templet_dict = {}
    product_I_dict = {}

    def __init__(self, container_manager):
        self.container_manager = container_manager
        # if 
        self.product_templet_dict = {
            'default':{
                'lot_head' : "0000-DFT-00", 
                'name' : 'default', 
                'flameable' : False, 
                'perishable' : False, 
                'container' : self.container_manager.container_dict['default'], 
                'weight' : None, 
                'inbound_frequency' : None, 
                'outbound_frequency' : 'high',
                },
            '01':{
                'lot_head' : "01-00", 
                'name' : '01', 
                'flameable' : False, 
                'perishable' : False, 
                'container' : self.container_manager.container_dict['default'], 
                'weight' : None, 
                'inbound_frequency' : 'high', 
                'outbound_frequency' : 'high',
                },
            '02':{
                'lot_head' : "02-00", 
                'name' : '02', 
                'flameable' : False, 
                'perishable' : False, 
                'container' : self.container_manager.container_dict['default'], 
                'weight' : None, 
                'inbound_frequency' : 'high', #'low'
                'outbound_frequency' : 'high', #'low'
                },
            '03':{
                'lot_head' : "03-00", 
                'name' : '03', 
                'flameable' : False, 
                'perishable' : False, 
                'container' : self.container_manager.container_dict['default'], 
                'weight' : None, 
                'inbound_frequency' : 'high', 
                'outbound_frequency' : 'high', #'low'
                },
            '04':{
                'lot_head' : "04-00", 
                'name' : '04', 
                'flameable' : False, 
                'perishable' : False, 
                'container' : self.container_manager.container_dict['default'], 
                'weight' : None, 
                'inbound_frequency' : 'high', 
                'outbound_frequency' : 'high',
                },
            
        }


    # def __init__(self, container_manager, saved_file):
    #     self.container_manager = container_manager
    #     pass


    def add_product_templet(self, 
                    # lot_head:str, 
                    product_name:str, 
                    # flameable:bool, 
                    # perishable:bool, 
                    # container:dict, 
                    # combination_indices:list, 
                    # weight, 
                    # inbound_frequency, 
                    # outbound_frequency
                    # **kwargs
                    ):
        kwargs = {
            # 'lot_head' : lot_head, 
            'product_name' : product_name,
        }

        print("아래의 값을 입력해주세요. 빈칸으로 비울 시(값을 입력하지 않고 엔터) \n"+ 
                " [초기값]이 적용됩니다.")
        for i,j in [
                    ['lot_head',            "제조 번호 전반부: str [0000-DFT-000n] \n"+ 
                                            ">> "],

                    # ['product_name',        "제품 이름 : str [Product_000n] \n"+ 
                    #                         ">> "],

                    ['flameable',           "화재 위험성 : 'high' or ['low'] \n"+ 
                                            ">> "],

                    ['perishable',          "화학적 변성 위험성 : 'high' or ['low'] \n"+ 
                                            ">> "],

                    ['container',           "상품 포장 규격 이름 : '이름' ['default] \n"+ 
                                            ">> "],

                    ['container_dimensions',"상품 포장 규격 크기 : x,y,z (mm) [300,200,200] \n"+ 
                                            ">> "],

                    ['combination_indices', "상품 세부 분류 (띄어쓰기 없이 ','로 분류. 단일 분류시 'x'): [0,0] \n"+ 
                                            ">> "],

                    ['weight',              "무개 (kg) : nn [None] \n"+ 
                                            ">> "],

                    ['inbound_frequency',   "입고 빈도 : 'high' or ['low'] \n"+ 
                                            ">> "],

                    ['outbound_frequency',  "출고 빈도 : ['high'] or 'low' \n"+ 
                                            ">> "],
            ]:
            input_val = input(j)
            if not input_val:
                if i == 'lot_head':
                    input_val = f"0000-DFT-{len(self.product_templet_dict.keys()):04d}"
                elif i == 'product_name':
                    input_val = f"Product_{len(self.product_templet_dict.keys()):04d}"
            kwargs[i] = input_val

            # product_manager.add_product_templet(lot_head, # =lot_head, 
            #                                     product_name, # =product_name,
            #                                     # flameable = flameable,
            #                                     # perishable = perishable,
            #                                     # container = container,
            #                                     # combination_indices = combination_indices,
            #                                     # weight = weight,
            #                                     # inbound_frequency = inbound_frequency,
            #                                     # outbound_frequency = outbound_frequency,
            #                                     **kwargs
            #                                     )

        # product_name = kwargs[0]
        if not kwargs['container']:
            kwargs['container'] = 'default'

        if (not kwargs['container'] in self.container_manager.container_dict.keys()):
            register_new_container = input(f"입력하신 포장 규격 '{kwargs.items()['container']}'은(는) 등록되어 있지 않습니다.\n"+ 
                  "새로 등록하시겠습니까? 신규 등록하지 않는 경우 기본값으로 등록됩니다.\n"+ 
                  "[yse / no] >> ")
            if register_new_container[0].lower() == 'y':
                  self.container_manager.add_container(kwargs['container']) # , **input_dict)

                  

            else:
                self.product_templet_dict[product_name]['container'] \
                    = self.container_manager.container_dict['default']
           

        self.product_templet_dict[product_name]= kwargs
            # { #lot_head/name
            # 'lot_head' : lot_head, 
            # 'name' : product_name, 
            # # 'flameable' : flameable, 
            # # 'perishable' : perishable, 
            
            # # 'container' : container, 
            # # 'weight' : weight, 
            # # 'inbound_frequency' : inbound_frequency, 
            # # 'outbound_frequency' : outbound_frequency, 
            # }
        
        # for key,val in kwargs.items():
        #     self.product_templet_dict[product_name][key] = val #lot_head/name
        
        if (self.product_templet_dict[product_name]['flameable'][0].lower() == 'l'): #lot_head/name
            self.product_templet_dict[product_name]['flameable']= False #lot_head/name

        if (self.product_templet_dict[product_name]['perishable'][0].lower() == 'l'): #lot_head/name
            self.product_templet_dict[product_name]['perishable']= False #lot_head/name

        # if not combination_indices:
        #     combination_indices = None
        # if not weight:
        #     weight = None
            
        if (not self.product_templet_dict[product_name]['inbound_frequency'] or #lot_head/name
        self.product_templet_dict[product_name]['inbound_frequency'].lower() == 'l'): #lot_head/name
            
            self.product_templet_dict[product_name]['inbound_frequency']=False #lot_head/name

        if (not self.product_templet_dict[product_name]['outbound_frequency']):  #lot_head/name
            self.product_templet_dict[product_name]['outbound_frequency']=True #lot_head/name

        elif (self.product_templet_dict[product_name]['outbound_frequency'].lower() == 'l'): #lot_head/name
            
            self.product_templet_dict[product_name]['outbound_frequency']=False #lot_head/name
  

    def register_item(self,
                    I_id,
                    # lot_head,
                    # lot_tail,
                    product_name, #lot_head/name
                    DOM:str,
                    manufactor:str,
                    WH_name:str,
                    Zone_name:str,
                    Area_name:str,
                    bin_location:list

                    ):
      
        
        lot_head = self.product_templet_dict[product_name]['lot_head']
        I_id = f"{len([i for i in self.product_I_dict.keys()if lot_head in i])+1:04d}"
        lot_tail = f"{DOM}-{I_id}"
        lot = f"{lot_head}-{lot_tail}"

        self.product_I_dict[lot]={
                'I_id'              : I_id,
                # 'lot_head'          : lot_head, #lot_head/name
                # 'lot_tail'          : lot_tail,
                'product_name'      : product_name, #lot_head/name
                'DOM'               : DOM,
                'manufactor'        : manufactor,
                'WH_name'           : WH_name,
                'Zone_name'         : Zone_name,
                'Area_name'         : Area_name,
                'bin_location'      : bin_location
            }
        
    
