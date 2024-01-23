class container_manager():
    container_dict = {
        'defalut':{
            'name'      : 'default',
            'length'    : 300, 
            'width'     : 200, 
            'height'    : 200,
            'gap'       : 200
                },
    }
    def __init__(self):
        pass

    def __init__(self, saved_file):
        pass

    def add_container(self, container_name:str, **kwargs):
        for key, val in kwargs.items():
            self.container_dict[container_name][key] = val

class product_manager():

    product_templet_dict = {}
    product_I_dict = {}

    def __init__(self, container_manager):
        self.container_manager = container_manager
        # if 
        self.product_templet_dict = {'default':{
            'lot_head' : 00000000, 
            'name' : 'default', 
            'flameable' : False, 
            'perishable' : False, 
            'container' : container_manager.container_dict['default'], 
            'weight' : None, 
            'inbound_frequency' : None, 
            'outbound_frequency' : 'high',
            }
        }

    def __init__(self, container_manager, saved_file):
        self.container_manager = container_manager
        pass

    def add_product_templet(self, 
                    lot_head:str, 
                    product_name:str, 
                    # flameable:bool, 
                    # perishable:bool, 
                    # container:dict, 
                    # combination_indices:list, 
                    # weight, 
                    # inbound_frequency, 
                    # outbound_frequency
                    **kwargs
                    ):
        
        if (not kwargs.items()['container'] in self.product_templet_dict[product_name]['container']):
            register_new_container = input(f"입력하신 포장 규격 '{kwargs.items()['container']}'은(는) 등록되어 있지 않습니다.\n"+ 
                  "새로 등록하시겠습니까? 신규 등록하지 않는 경우 기본값으로 등록됩니다.\n"+ 
                  ">> ")
            if register_new_container:
                input_dict = {}
                print("아래의 값을 입력해주세요. 빈칸으로 비울 시(값을 입력하지 않고 엔터) \n"+ 
                        " 초기값이 적용됩니다.")
                name = input('규격 이름' + ">> ")
                for i,j in [[   'length'    , '길이 (mm)' + ">> "], 
                            [   'width'     , '너비 (mm)' + ">> "], 
                            [   'height'    , '높이 (mm)' + ">> "],
                            [   'gap'       , '최대 배치 간격 (전후 좌우 동일) (mm)' + ">> "]
                ]:
                  input_dict[i] = input(j)    
                  container_manager.add_container(name, input_dict)

            self.product_templet_dict[product_name]\
                ['container'] = self.container_manager.container_dict['defalut']
           

        self.product_templet_dict[product_name]={ #lot_head/name
            'lot_head' : lot_head, 
            'name' : product_name, 
            # 'flameable' : flameable, 
            # 'perishable' : perishable, 
            
            # 'container' : container, 
            # 'weight' : weight, 
            # 'inbound_frequency' : inbound_frequency, 
            # 'outbound_frequency' : outbound_frequency, 
            }
        
        for key,val in kwargs.items():
            self.product_templet_dict[product_name][key] = val #lot_head/name
        
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

        if (not self.product_templet_dict[product_name]['outbound_frequency'] or #lot_head/name
        self.product_templet_dict[product_name]['outbound_frequency'].lower() == 'l'): #lot_head/name
            
            self.product_templet_dict[product_name]['outbound_frequency']=False #lot_head/name

        

    def add_product(self,
                    product_name, #lot_head/name
                    DOM:str,
                    manufactor,
                    # lot_tail,
                    bin_location
                    ):
        lot_head = self.product_templet_dict[product_name]['lot_head']

        lot_tail = DOM + f"{len([i for i in self.product_I_dict.keys() 
                                if lot_head in i]):04d}"
        self.product_I_dict[ 
            lot_head #lot_head/name
            # self.product_templet_dict[product_name]['lot_head']
            # +self.product_I_dict[product_name]
            ] ={
                'lot_head'      : lot_head, #lot_head/name
                'product_name'  : product_name, #lot_head/name
                'DOM'           : DOM,
                'manufactor'    : manufactor,
                'lot_tail'      : lot_tail,
                'bin_location'  : bin_location
            }
