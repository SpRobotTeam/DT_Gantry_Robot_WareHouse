# import sys, os
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from WCS import SPWCS
import random as rand
import time
# from MW import PLC_com
# import pprint

web = False
manual = True


class main(SPWCS.GantryWCS):
    def multiple_inbound(self, name, num):
        for _ in range(num):
            res = self.Inbound(product_name=name)
            if res:
                return res

    def multiple_outbound(self, name, num = None):
        if name in self.product_templet_dict.keys():
            lot = self.product_templet_dict[name]['lot_head']
        else:
            print(f"{name}은 등록되지 않은 상품입니다.")
            return 1
        if not num:
            num = len([i for i in self.WH_dict['WH_DT'].Zone_dict['Zone_Gantry'].Area_dict['Area_01'].inventory.keys() if lot in i])
        
        while num > 0 and len([i for i in self.WH_dict['WH_DT'].Zone_dict['Zone_Gantry'].Area_dict['Area_01'].inventory.keys() if lot in i]) :
            product = rand.choice(list(self.product_I_dict.keys()))
            if 'WH_name' in self.product_I_dict[product].keys():
                self.Outbound(product)
                num -= 1

    # modbus_com = PLC_com.plc_com
    def reset(self, container_name = None):
        self.WH_dict = {}
        self.default_setting(container_name=container_name)
        self.product_I_dict = {}
    
    def get_info(self, args)->dict|list:
        '''
        외부에서 클래스 내부 정보를 찾을 때 사용하는 함수

        [p(roduct)  ] -> dict   or

        [t(emplet)  ] -> dict   or

        [c(ontainer)] -> dict   or

        [w(h)       , WH_name] -> dict   or

        [z(one)     , WH_name, Zone_name] -> dict   or

        [a(rea)     , WH_name, Zone_name, Area_name] -> dict   or

        [i(nventory), WH_name, Zone_name, Area_name] -> dict   or

        [g(rid)     , WH_name, Zone_name, Area_name] -> list   
        '''
        try:
            if args[0].lower()[0] == 'product'[0]: # product_I_dict
                target = self.product_I_dict

            elif args[0].lower()[0] == 'templet'[0]: # product_templet_dict
                target = self.product_templet_dict
            
            elif args[0].lower()[0] == 'container'[0]: # container_dict
                target = self.container_dict

            elif args[0].lower()[0] == 'WH'.lower()[0]: # WH_dict
                target = self.WH_dict[args[1]]

            elif args[0].lower()[0] == 'Zone'.lower()[0]: # Zone_dict
                target = self.WH_dict[args[1]].Zone_dict[args[2]]

            elif args[0].lower()[0] == 'Area'.lower()[0]: # Area_dict
                target = self.WH_dict[args[1]].Zone_dict[args[2]].Area_dict[args[3]]

            elif args[0].lower()[0] == 'inventory'[0]: # ... Area.inventory
                target = self.WH_dict[args[1]].Zone_dict[args[2]].Area_dict[args[3]].inventory

            elif args[0].lower()[0] == 'grid'[0]: # ... Area.grid
                target = self.WH_dict[args[1]].Zone_dict[args[2]].Area_dict[args[3]].grid

            else:
                target = []

        except :
            if args[0].lower()[0] == 'grid'[0]: # ... Area.grid
                target = []
            
            else:
                target = {}

        finally:
            return target
        


    
    def default_setting(self, container_name = None):
        

        self.WH_name   = 'WH_DT'
        self.Zone_name = 'Zone_Gantry'
        self.Area_name = 'Area_01'

        self.add_WH({
            # self = SPWCS.GantryWCS()
            'WH_name':self.WH_name,
        })

        if not container_name:
            container_name_input = input("사용할 컨테이너의 이름을 입력해주세요. [기본값 'DT']" + "\n>> ")
            container_name = container_name_input if container_name_input else 'DT'
            
        if not container_name in self.container_dict.keys():
            self.add_container(container_name=container_name)

        self.WareHouse = self.WH_dict[self.WH_name]
        self.WareHouse.add_zone({
            'Zone_name'      : self.Zone_name,
            'container'      : self.container_dict[container_name],
        })
        
        self.Zone = self.WareHouse.Zone_dict[self.Zone_name]
        self.Zone.add_area({
            'Area_name' : 'Gantry',
            'origin'    : [0,1,0]  ,  
            'col'       :  1 , 
            'row'       :  1 , 
            'heigth'    :  1 , 
            'grid_type' :  'r' 
        })
        self.Zone.add_area({
            'Area_name' : 'In',
            'origin'    : [0,0,0]  ,  
            'col'       :  1 , 
            'row'       :  1 , 
            'heigth'    :  1 , 
            'grid_type' :  'r' 
        })
        self.Zone.add_area({
            'Area_name' : 'Out',
            'origin'    : [0,0,0]  ,  
            'col'       :  1 , 
            'row'       :  1 , 
            'heigth'    :  1 , 
            'grid_type' :  'r' 
        })
        self.Zone.add_area({
            'Area_name' : 'Area_01',
            'origin'    : [1,1,1]  ,  
            'col'       :  4 , 
            'row'       :  4 , 
            'heigth'    :  2 , 
            'grid_type' :  'r' 
        })

        



if __name__ == "__main__":

    name = 'default'

    if web:
        pass
    else:
        SPDTw = main()
        if manual:
            SPDTw.default_setting()

            while True:
                
                command_input = input(
                    "명령을 입력하세요. "+
                    "n [상품 이름 : 기본값='default'] : 상품명이 'name'인 상품 선택 "+
                    "i [정수 갯수 : 기본값=8] : [num]만큼 입고, "+
                    "o [정수 갯수 : 기본값=전채] : [num] 만큼 무작위 출고," +
                    "p [마지막 lot 번호 : 기본값=가장 오래된 상자] : 특정 상자 출고, "+
                    # "r [num : 기본값=0(번 부터 끝까지)] : 창고 정리, "+
                    "l : 구역 물품 리스트 출력, "+
                    "c : 종료"+
                    "\n>>"
                    )
                command = num = None
                

                try:
                    arg_list = command_input.split(' ')
                    for arg in arg_list:
                        if not arg:
                            continue
                        elif not command:
                            command = arg[0].lower()
                        elif arg.isdecimal():
                            num = int(arg)
                        else:
                            name = arg
                    
                    if command == 'n':
                        # name = arg
                        # SPWCS.GantryWCS.Inbound(
                        #     self = SPDTw,
                        #     product_name=name,
                        #     WH_name=SPDTw.WH_name,
                        #     Zone_name=SPDTw.Zone_name,
                        #     Area_name=SPDTw.Area_name
                        # )
                        if name not in SPDTw.product_templet_dict.keys():
                            SPDTw.add_product_templet(product_name=name)

                    if command == 'i':
                        
                        if not num:
                            num = 8
                        SPDTw.multiple_inbound(name, num)                
                    
                    if command == 'o':
                        if not num:
                            num = len(list([i for i in SPDTw.WH_dict['WH_DT'].Zone_dict['Zone_Gantry'].Area_dict['Area_01'].inventory.keys() if lot in i]))
                        SPDTw.multiple_outbound(name, num)

                    if command == 'p':
                        lot = None
                        if num:
                            for i in list(SPDTw.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict['Area_01'].inventory.keys()):
                                if f"{num:04d}" in i[-4:]:
                                    lot = i
                                    break
                        else:
                            lot = list(SPDTw.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict['Area_01'].inventory.keys())[0]
                        
                        if lot:
                            SPWCS.GantryWCS.Outbound(self=SPDTw, lot=lot)
                        else:
                            f"입력 {num:04d}와 일치하는 상품이 없습니다."

                    # if command == 'r':
                    #     if not num:
                    #         num = 0
                    #     WCS.GantryWCS.rearrange_area(self=SPDTw, WH_name=WH_name, Zone_name=Zone_name, Area_name=Area_name, offset=num, HEIGHT=Zone.Area_dict[Area_name].HEIGHT)
                
                    if command == 'l':
                        print(SPDTw.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict['Area_01'].grid)


                    if command == 'c':
                        print("WCS 종료 중 ... ")
                        break
                except:
                    pass


            
                
            
        else:
            SPDTw = SPWCS.GantryWCS()
            # SPDTw.__init__()
            SPDTw.add_default_WH()

            box_amount = 16

            for _ in range(box_amount):
                SPDTw.Inbound()

            _ = 0
            while _ < box_amount:
                product = rand.choice(list(SPDTw.product_I_dict.keys()))
                if 'WH_name' in SPDTw.product_I_dict[product].keys():
                    SPDTw.Outbound(product)
                    _ += 1
                

            print("test_fin")


else:
    SPDTw = main()