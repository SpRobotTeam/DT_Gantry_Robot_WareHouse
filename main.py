# import sys, os
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from WCS import WCS
import random as rand
# import pprint

manual = True

def inbound(num = 16):
    for _ in range(num):
        res = wcs_DT.Inbound()
        if res:
            return res

def outbound(num = None):
    if not num:
        num = len(wcs_DT.WH_dict['WH_DT'].Zone_dict['Zone_Gantry'].Area_dict['Area_01'].inventory.keys())
    
    while num > 0 and len(wcs_DT.WH_dict['WH_DT'].Zone_dict['Zone_Gantry'].Area_dict['Area_01'].inventory.keys()) :
        product = rand.choice(list(wcs_DT.product_I_dict.keys()))
        if 'WH_name' in wcs_DT.product_I_dict[product].keys():
            wcs_DT.Outbound(product)
            num -= 1



if manual:
    WH_name = 'WH_DT'
    Zone_name = 'Zone_Gantry'

    wcs_DT = WCS.GantryWCS()
    wcs_DT.add_WH({
        'WH_name':WH_name,
    })


    container_name = None
    while not container_name:
        container_name_input = input("사용할 컨테이너의 이름을 입력해주세요. [기본값 'DT']" + "\n>> ")
        container_name = container_name_input if container_name_input else 'DT'
    wcs_DT.add_container(container_name=container_name)

    WareHouse = wcs_DT.WH_dict[WH_name]
    WareHouse.add_zone({
        'Zone_name'      : Zone_name,
        'container' : wcs_DT.container_dict[container_name],
    })

    Zone = WareHouse.Zone_dict[Zone_name]
    Zone.add_area({
        'Area_name' : 'Gantry',
        'origin'    : [0,1,0]  ,  
        'col'       :  1 , 
        'row'       :  1 , 
        'heigth'    :  1 , 
        'grid_type' :  'r' 
    })
    Zone.add_area({
        'Area_name' : 'In',
        'origin'    : [0,15,0]  ,  
        'col'       :  1 , 
        'row'       :  1 , 
        'heigth'    :  1 , 
        'grid_type' :  'r' 
    })
    Zone.add_area({
        'Area_name' : 'Out',
        'origin'    : [0,15,0]  ,  
        'col'       :  1 , 
        'row'       :  1 , 
        'heigth'    :  1 , 
        'grid_type' :  'r' 
    })
    Zone.add_area({
        'Area_name' : 'Area_01',
        'origin'    : [1,0,0]  ,  
        'col'       :  4 , 
        'row'       :  4 , 
        'heigth'    :  2 , 
        'grid_type' :  'r' 
    })

    while True:
        
        command_input = input(
            "명령을 입력하세요. i [num : 기본값 8] : [num]만큼 입고, o [num : 기본값 전채] : [num] 만큼 출고, l : 구역 물품 리스트 출력, c : 종료"+
            "\n>>"
            )
        command = num = None
        
        try:
            p = command_input.split(' ')
            for c in p:
                if not c:
                    continue
                elif not command:
                    command = c[0].lower()
                elif c.isdecimal():
                    num = int(c)
            
            if command == 'i':
                
                if not num:
                    num = 8
                inbound(num)                
            
            if command == 'o':
                if not num:
                    num = len(list(wcs_DT.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict['Area_01'].inventory.keys()))
                outbound(num)

            if command == 'l':
                print(wcs_DT.WH_dict[WH_name].Zone_dict[Zone_name].Area_dict['Area_01'].grid)

            if command == 'c':
                print("WCS 종료 중 ... ")
                break
        except:
            pass


    
        
    
else:
    wcs_DT = WCS.GantryWCS()
    # wcs_DT.__init__()
    wcs_DT.add_default_WH()

    box_amount = 16

    for _ in range(box_amount):
        wcs_DT.Inbound()

    _ = 0
    while _ < box_amount:
        product = rand.choice(list(wcs_DT.product_I_dict.keys()))
        if 'WH_name' in wcs_DT.product_I_dict[product].keys():
            wcs_DT.Outbound(product)
            _ += 1
        

    print("test_fin")