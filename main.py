# import sys, os
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from WCS import WCS
import random as rand

manual = False

if manual:
    WH_name = 'WH_DT'
    Zone_name = 'Zone_Gnatry'

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
        'col'       :  4 , 
        'row'       :  4 , 
        'heigth'    :  4 , 
        'grid_type' :  'r' 
    })
    Zone.add_area({
        'area_name' : 'In',
        'origin'    : [0,15,0]  ,  
        'col'       :  4 , 
        'row'       :  4 , 
        'heigth'    :  4 , 
        'grid_type' :  'r' 
    })
    Zone.add_area({
        'area_name' : 'Out',
        'origin'    : [0,15,0]  ,  
        'col'       :  4 , 
        'row'       :  4 , 
        'heigth'    :  4 , 
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



    box_amount = 16

    for _ in range(box_amount):
        wcs_DT.Inbound()

    _ = 0
    while _ <= box_amount:
        product = rand.choice(list(wcs_DT.product_I_dict.keys()))
        if 'WH_name' in wcs_DT.product_I_dict[product].keys():
            wcs_DT.Outbound(product)
            _ += 1
        

    print("test_fin")

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