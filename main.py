# import sys, os
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from WCS import SPWCS
import random as rand
import time
# from MW import PLC_com
# import pprint
import os, sys
import subprocess, asyncio # concurrent.futures
import csv

from ERROR.error import NotEnoughSpaceError, SimError, ProductNotExistError

from SIM.EVAL.evaluator import Evaluator

web = False
manual = False

LEAST_MISSION_LENGTH = 100000

PYTHON_NAME = "python" if 'nt' in os.name else 'python3'

class main(SPWCS.GantryWCS):
    def __init__(self, op_mode = None):  
        
        # self.sim_RoboDK()
        # os.system(
        #     f"{PYTHON_NAME} {os.path.dirname(os.path.realpath(__file__))}/SIM/RoboDK/plc_motion006.py"
        #     )

        try:
            if op_mode.isdigit():
                self.op_mode = int(op_mode)
            elif op_mode:
                self.op_mode = op_mode.lower()
        except Exception:
            self.op_mode = None
        
        SPWCS.GantryWCS.__init__(self, self.op_mode)

    # async def sim_RoboDK(self):
    #     subprocess.run(
    #         arg=f"{PYTHON_NAME} {os.path.dirname(os.path.realpath(__file__))}/SIM/RoboDK/plc_motion006.py",
    #         shell=True, 
    #         )


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
    
    def get_info(self, args):#->dict|list:
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
            # 'origin'    : [21,21,0],
            # 'origin'    : [4,4,0]  ,  # 
            'origin'    : [0,0,0],
            'col'       :  1 , 
            'row'       :  1 , 
            'heigth'    :  1 , 
            'grid_type' :  'r' 
        })
        self.Zone.add_area({
            'Area_name' : 'Area_01',
            'origin'    : [1,1,1]  ,  
            'col'       :  7,    # 7,   # 20,   # 4
            'row'       :  6,    # 6,   # 20,   # 4
            'heigth'    :  5,    # 2
            # 'col'       :  3 ,  #
            # 'row'       :  3 ,  #
            # 'heigth'    :  4 ,  #
            'grid_type' :  'r' 
        })

        



if __name__ == "__main__":

    name = 'default'

    op_input:str = input(
        "실행 모드를 선택하세요. \n"+
        "선택 가능한 옵션 : \n"+
        '"S"             - 알고리즘 평가 기준 생성 모드\n'+
        '"N"             - 알고리즘 테스트 모드 (시뮬레이션 없음)\n'+
        '""'
        "(그외 모든 경우) - 일반 모드\n"+
        " >> "
        )
    
    if op_input.isdigit():
        op_mode = int(op_input)
    elif op_input:
        op_mode = op_input.lower()
        if op_mode == 'n':
            op_mode = 'no_sim'
    else:
        op_mode = None
        manual = True
    
    file_name = None
    try:
        if op_mode[0].lower() in ['s', 'n']:
            if op_mode == 's':
                print("알고리즘 평가 기준 생성 모드로 WCS를 실행합니다!")
            elif op_mode == 'n':
                print("알고리즘 테스트 모드(모드버스 무효화)로 WCS를 실행합니다!")
                
            # manual = False
            seed = None
            while not seed:
                input_seed:str = input(
                    "테스트에 사용할 SEED를 입력하세요 (최대 6자리 int)\n"+
                    " >> "
                    )[-6:]
                if input_seed.isdigit():
                    seed = int(input_seed)
            
            file_name = f"{os.path.dirname(os.path.realpath(__file__))}/SIM/EVAL/mission_list/mission_list_SEED-{seed:06d}.csv"

            if not os.path.isfile(file_name):
                
                # os.system(f"{PYTHON_NAME} {os.path.dirname(os.path.realpath(__file__))}/SIM/EVAL/mission_list_generator.py {seed} {LEAST_MISSION_LENGTH*2}")
                with open(os.devnull, 'wb') as devnull:
                    subprocess.check_call([PYTHON_NAME, f"{os.path.dirname(os.path.realpath(__file__))}/SIM/EVAL/mission_list_generator.py", str(seed), str(LEAST_MISSION_LENGTH*2)],
                                          stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                time.sleep(5)

    except:
        op_mode = None


    if web:
        pass
    else:
        SPDTw = main(op_mode=op_mode)
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
                            num = len(list([i for i in SPDTw.WH_dict['WH_DT'].Zone_dict['Zone_Gantry'].Area_dict['Area_01'].inventory.keys()]))
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
            # SPDTw.__init__()
            SPDTw.default_setting(container_name='default')
            

            unit_time_past = 0
            sum_distance = [0,0]
            GANTRY_MOVING_SPEED = [1,1]

            mission_length = 0
            with open(file_name,'r', newline='') as csv_editor:
                reader = csv.reader(csv_editor)
                for line in reader:
                    mission_length += 1

            if mission_length < LEAST_MISSION_LENGTH*2:
                # os.system(f"{PYTHON_NAME} {os.path.dirname(os.path.realpath(__file__))}/SIM/EVAL/mission_list_generator.py {seed} {LEAST_MISSION_LENGTH*2}")
                subprocess.check_call(["{PYTHON_NAME}", f"{os.path.dirname(os.path.realpath(__file__))}/SIM/EVAL/mission_list_generator.py", str(seed), str(LEAST_MISSION_LENGTH*2)],
                                          stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                mission_length = LEAST_MISSION_LENGTH

            mission_offset = 0
            # for _ in range(mission_length):
            for _ in range(LEAST_MISSION_LENGTH):
                
                action = product_name = dom = wait_time = None

                with open(file_name,'r', newline='') as csv_editor:
                    line_index = 0
                    mission_list = csv.reader(csv_editor)
                    for line in mission_list:
                        if line_index == _ + mission_offset:
                            action = line[1]
                        
                            if action in ['IN', 'OUT']:
                                product_name = f"{int(line[2]):02d}"
                                if action == 'IN':
                                    dom = line[3]
                            elif action in ['WAIT']:
                                wait_time = line[2]
                            break
                        else:
                            line_index += 1
                
                if action == 'IN':
                    try:
                        moved_distance = SPDTw.Inbound(product_name=product_name, DOM=dom, testing_mode = True)
                        sum_distance = [m+s for m,s in zip(moved_distance,sum_distance)]
                        unit_time_past += sum([d*s for d,s in zip(moved_distance, GANTRY_MOVING_SPEED)])
                    except NotEnoughSpaceError: # 공간 부족 시
                        mission_offset += 1 # 다음 미션으로 (현 미션 스킵)
                        print("입고 명령 무시 : 창고 공간 부족")
                        continue
                elif action == 'OUT':
                    try:
                        moved_distance = SPDTw.Outbound(product_name=product_name, testing_mode = 1)
                    except ProductNotExistError:
                        print("출고 명령 무시 : 해당 품목의 상품 없음")
                        continue
                    sum_distance = [m+s for m,s in zip(moved_distance,sum_distance)]
                    unit_time_past += sum([d*s for d,s in zip(moved_distance, GANTRY_MOVING_SPEED)])
                elif action == 'WAIT':
                    # unit_time_past += wait_time
                    pass
                
                if action == 'WAIT':
                    print(
                        f"mission_{_+1-mission_offset} fin (mission list # {_})\n"+
                        f"Waiting time : {wait_time}"+
                        f"Total Unit time past : {unit_time_past}\n"+
                        "-----------------------------------------------------------"+"\n"
                        )
                else:
                    print(
                        f"\nMission_{_+1-mission_offset} fin! fin (mission list # {_})\n"+
                        f"moved_distance : {moved_distance}\n"+
                        f"Unit time past : {sum([d*s for d,s in zip(moved_distance, GANTRY_MOVING_SPEED)])}\n"+
                        f"Total Unit time past : {unit_time_past}\n"+
                        "-----------------------------------------------------------"+"\n"
                        )
                    
            eval_score = Evaluator(mode=op_mode, SEED=seed, mission_length = LEAST_MISSION_LENGTH)
            final_score, time_score, position_score, average_height = eval_score.evaluate(
                time_past=unit_time_past, 
                grid_list=SPDTw.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict['Area_01'].grid
                )

            print(
                f"test_fin \n"+
                f"Sum of moved distance : {sum_distance} \n"+
                f"Total Unit time past  : {unit_time_past}\n" +
                f"Standard deviation  : {average_height}\n" +
                "-----------------------------------------------------------"+"\n"+
                f"time_score     : {time_score*100:.2f}%\n"+
                f"position_score : {position_score:.2f}\n"+
                f"total_score    : {final_score*100:.2f}%\n"
                "___________________________________________________________"+"\n"
                  )
            
            # time.sleep(5)


else:
    SPDTw = main()