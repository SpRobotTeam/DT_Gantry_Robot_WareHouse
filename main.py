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
    def inbound(self, num):
        for _ in range(num):
            res = self.wcs_DT.Inbound()
            if res:
                return res

    def outbound(self, num = None):
        if not num:
            num = len(self.wcs_DT.WH_dict['WH_DT'].Zone_dict['Zone_Gantry'].Area_dict['Area_01'].inventory.keys())
        
        while num > 0 and len(self.wcs_DT.WH_dict['WH_DT'].Zone_dict['Zone_Gantry'].Area_dict['Area_01'].inventory.keys()) :
            product = rand.choice(list(self.wcs_DT.product_I_dict.keys()))
            if 'WH_name' in self.wcs_DT.product_I_dict[product].keys():
                self.wcs_DT.Outbound(product)
                num -= 1

    # modbus_com = PLC_com.plc_com
    def reset(self, container_name = None):
        self.WH_dict = {}
        self.default_setting(container_name=container_name)
        self.wcs_DT.product_I_dict = {}
    
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

        self.wcs_DT = SPWCS.GantryWCS()
        self.wcs_DT.add_WH({
            'WH_name':self.WH_name,
        })

        if not container_name:
            container_name_input = input("사용할 컨테이너의 이름을 입력해주세요. [기본값 'DT']" + "\n>> ")
            container_name = container_name_input if container_name_input else 'DT'
            
        if not container_name in self.wcs_DT.container_dict.keys():
            self.wcs_DT.add_container(container_name=container_name)

        self.WareHouse = self.wcs_DT.WH_dict[self.WH_name]
        self.WareHouse.add_zone({
            'Zone_name'      : self.Zone_name,
            'container'      : self.wcs_DT.container_dict[container_name],
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


    if web:
        pass
    else:
        SPDTw = main()
        if manual:
            SPDTw.default_setting()

            while True:
                
                command_input = input(
                    "명령을 입력하세요. "+
                    "i [num : 기본값=8] : [num]만큼 입고, "+
                    "o [num : 기본값=전채] : [num] 만큼 출고," +
                    "p [num : 기본값=가장 오래된 상자] : 특정 상자 출고, "+
                    # "r [num : 기본값=0(번 부터 끝까지)] : 창고 정리, "+
                    "l : 구역 물품 리스트 출력, "+
                    "n [name : 기본값='default'] : 상품명이 'name'인 상품 입고 "+
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
                    
                    if command == 'i':
                        
                        if not num:
                            num = 8
                        SPDTw.inbound(num)                
                    
                    if command == 'o':
                        if not num:
                            num = len(list(SPDTw.wcs_DT.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict['Area_01'].inventory.keys()))
                        SPDTw.outbound(num)

                    if command == 'p':
                        lot = None
                        if num:
                            for i in list(SPDTw.wcs_DT.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict['Area_01'].inventory.keys()):
                                if f"{num:04d}" in i[-4:]:
                                    lot = i
                                    break
                        else:
                            lot = list(SPDTw.wcs_DT.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict['Area_01'].inventory.keys())[0]
                        
                        if lot:
                            SPWCS.GantryWCS.Outbound(self=SPDTw.wcs_DT, lot=lot)
                        else:
                            f"입력 {num:04d}와 일치하는 상품이 없습니다."

                    # if command == 'r':
                    #     if not num:
                    #         num = 0
                    #     WCS.GantryWCS.rearrange_area(self=SPDTw.wcs_DT, WH_name=WH_name, Zone_name=Zone_name, Area_name=Area_name, offset=num, HEIGHT=Zone.Area_dict[Area_name].HEIGHT)
                
                    if command == 'l':
                        print(SPDTw.wcs_DT.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict['Area_01'].grid)

                    if command == 'n':
                        SPWCS.GantryWCS.Inbound(
                            self = SPDTw.wcs_DT,
                            product_name=name,
                            WH_name=SPDTw.WH_name,
                            Zone_name=SPDTw.Zone_name,
                            Area_name=SPDTw.Area_name
                        )

                    if command == 'c':
                        print("WCS 종료 중 ... ")
                        break
                except:
                    pass


            
                
            
        else:
            SPDTw.wcs_DT = SPWCS.GantryWCS()
            # SPDTw.wcs_DT.__init__()
            SPDTw.wcs_DT.add_default_WH()

            box_amount = 16

            for _ in range(box_amount):
                SPDTw.wcs_DT.Inbound()

            _ = 0
            while _ < box_amount:
                product = rand.choice(list(SPDTw.wcs_DT.product_I_dict.keys()))
                if 'WH_name' in SPDTw.wcs_DT.product_I_dict[product].keys():
                    SPDTw.wcs_DT.Outbound(product)
                    _ += 1
                

            print("test_fin")


else:
    SPDTw = main()