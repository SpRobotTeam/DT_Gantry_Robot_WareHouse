# import sys, os
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from WCS import WCS
import random as rand

manual = True

def inbound(num = 16):
    for _ in range(num):
        wcs_DT.Inbound()

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
    wcs_DT.add_WH(**{
        'name':WH_name,
    })


    container_name = None
    while not container_name:
        container_name = input("사용할 컨테이너의 이름을 입력해주세요." + "\n>> ")
    wcs_DT.add_container(container_name=container_name)

    WareHouse = wcs_DT.WH_dict[WH_name]
    WareHouse.add_zone({
        'name'      : Zone_name,
        'container' : wcs_DT.container_dict[container_name],
    })

    Zone = WareHouse.Zone_dict[Zone_name]
    Zone.add_area({
        'area_name' : 'Gantry',
        'origin'    : [0,1,0]  ,  
        'col'       :  1 , 
        'row'       :  1 , 
        'heigth'    :  1 , 
        'grid_type' :  'r' 
    })
    Zone.add_area({
        'area_name' : 'In',
        'origin'    : [0,15,0]  ,  
        'col'       :  1 , 
        'row'       :  1 , 
        'heigth'    :  1 , 
        'grid_type' :  'r' 
    })
    Zone.add_area({
        'area_name' : 'Out',
        'origin'    : [0,15,0]  ,  
        'col'       :  1 , 
        'row'       :  1 , 
        'heigth'    :  1 , 
        'grid_type' :  'r' 
    })
    Zone.add_area({
        'area_name' : 'Area_01',
        'origin'    : [1,0,0]  ,  
        'col'       :  4 , 
        'row'       :  4 , 
        'heigth'    :  4 , 
        'grid_type' :  'r' 
    })

    command = ''
    while True:
        command = input(
            "명령을 입력하세요. i [num] : [num]만큼 입고, o [num] : [num] 만큼 출고, c : 종료"+
            "\n>>"
            )

        if command :
            if command[0].lower() == 'c':
                print("WCS 종료 중 ... ")
                break
        p = command.split(" ")
        if len(p) != 1:
            try:
                num = int(p[1])
                if command[0].lower() == 'i':
                    inbound(num)
                
                if command[0].lower() == 'o':
                    outbound(num)
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