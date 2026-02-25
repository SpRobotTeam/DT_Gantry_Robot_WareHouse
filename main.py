import logging.handlers
from WCS import SPWCS
import random as rand
import time
import os, sys, pathlib
import subprocess
import csv

from ERROR.error import NotEnoughSpaceError, SimError, ProductNotExistError

from SIM.EVAL.evaluator import Evaluator
from SIM.EVAL.visualizer import VizCollector

import logging
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
pathlib.Path("./logs").mkdir(parents=True, exist_ok=True)
pathlib.Path("./logs/main.log").touch()
log_file_handler = logging.handlers.RotatingFileHandler(filename="./logs/main.log", 
                                    mode="a",
                                    backupCount= 3,
                                    maxBytes= 1024*125,
                                    encoding='utf-8'
                                    )
log_formater = logging.Formatter("{asctime} {levelname} {filename}>{funcName} {message}", style='{')
log_file_handler.setFormatter(log_formater)
logger.addHandler(log_file_handler)

log_streamer = logging.StreamHandler()
log_streamer.setFormatter(log_formater)
logger.addHandler(log_streamer)

logger.info("______________________________________________________________________\nProgram start")

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

    def multiple_inbound(self, name, num):
        for _ in range(num):
            res = self.Inbound(product_name=name)
            if res:
                return res

    def multiple_outbound(self, name, num = None):
        if name in self.product_templet_dict.keys():
            lot = self.product_templet_dict[name]['lot_head']
        else:
            logger.info(f"{name}은 등록되지 않은 상품입니다.")
            return 1
        if not num:
            num = len([i for i in self.WH_dict['WH_DT'].Zone_dict['Zone_Gantry'].Area_dict['Area_01'].inventory.keys() if lot in i])
        
        while num > 0 and len([i for i in self.WH_dict['WH_DT'].Zone_dict['Zone_Gantry'].Area_dict['Area_01'].inventory.keys() if lot in i]) :
            product = rand.choice(list(self.product_I_dict.keys()))
            if 'WH_name' in self.product_I_dict[product].keys():
                self.Outbound(product)
                num -= 1

    def reset(self, container_name = None):
        self.WH_dict = {}
        self.default_setting(container_name=container_name)
        self.product_I_dict = {}
        self._registered_count = {}
        self._lots_by_product = {}
        self._outbound_count = {}
        self._total_outbound = 0
        self._recent_outbound.clear()
        self._recent_outbound_count = {}
    
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
            'sim_skip'       : self.sim_skip,
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
            'col'       :  20,   # 7,   # 20,   # 4
            'row'       :  20,   # 6,   # 20,   # 4
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
        if op_mode in ['n','ㅜ']:
            op_mode = 'n'
        elif op_mode in ['s', 'ㄴ']:
            op_mode = 's'
    else:
        op_mode = None
        manual = True
    
    file_name = None
    algo_mode = 'FF'
    try:
        if op_mode[0].lower() in ['s', 'n']:
            if op_mode == 's':
                logger.info("알고리즘 평가 기준 생성 모드로 WCS를 실행합니다!")
            elif op_mode[0].lower() == 'n':
                logger.info("알고리즘 테스트 모드(모드버스 무효화)로 WCS를 실행합니다!")

            # manual = False
            seed = None
            while not seed:
                input_seed:str = input(
                    "테스트에 사용할 SEED를 입력하세요 (최대 6자리 int)\n"+
                    " >> "
                    )[-6:]
                if input_seed.isdigit():
                    seed = int(input_seed)

            algo_input = input(
                "배치 알고리즘을 선택하세요:\n"+
                "  FF  - First-Fit (기본)\n"+
                "  RL  - 실시간 학습 (출고 빈도 기반 배치)\n"+
                "  LA  - 미리보기 (미션 리스트 사전 분석)\n"+
                "  RA  - 최근 출고 기반 적응형 (연속 스코어링)\n"+
                " >> "
                )
            algo_mode = algo_input.strip().upper()
            if algo_mode not in ('FF', 'RL', 'LA', 'RA'):
                algo_mode = 'FF'
            logger.info(f"배치 알고리즘: {algo_mode}")

            file_name = f"{os.path.dirname(os.path.realpath(__file__))}/SIM/EVAL/mission_list/mission_list_SEED-{seed:06d}.csv"

            if not os.path.isfile(file_name):

                print(f"미션 리스트 생성 중 (SEED={seed:06d}, {LEAST_MISSION_LENGTH*2}건) ...")
                subprocess.check_call([PYTHON_NAME, f"{os.path.dirname(os.path.realpath(__file__))}/SIM/EVAL/mission_list_generator.py", str(seed), str(LEAST_MISSION_LENGTH*2)])
                print("미션 리스트 생성 완료!")
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
                            logger.info(f"입력 {num:04d}와 일치하는 상품이 없습니다.")

                    # if command == 'r':
                    #     if not num:
                    #         num = 0
                    #     WCS.GantryWCS.rearrange_area(self=SPDTw, WH_name=WH_name, Zone_name=Zone_name, Area_name=Area_name, offset=num, HEIGHT=Zone.Area_dict[Area_name].HEIGHT)
                
                    if command == 'l':
                        logger.info(SPDTw.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict['Area_01'].grid)


                    if command == 'c':
                        logger.info("WCS 종료 중 ... ")
                        break
                except:
                    pass


        
        else:
            # SPDTw.__init__()
            print("창고 초기화 중 ...")
            SPDTw.mode = algo_mode
            SPDTw.default_setting(container_name='default')
            print(f"창고 초기화 완료! (알고리즘: {algo_mode})")

            unit_time_past = 0
            sum_distance = [0,0]
            GANTRY_MOVING_SPEED = [1,1]

            print("미션 리스트 로딩 중 ...")
            mission_length = 0
            with open(file_name,'r', newline='') as csv_editor:
                reader = csv.reader(csv_editor)
                for line in reader:
                    mission_length += 1

            if mission_length < LEAST_MISSION_LENGTH*2:
                print(f"미션 리스트 재생성 중 ({LEAST_MISSION_LENGTH*2}건) ...")
                subprocess.check_call([PYTHON_NAME, f"{os.path.dirname(os.path.realpath(__file__))}/SIM/EVAL/mission_list_generator.py", str(seed), str(LEAST_MISSION_LENGTH*2)])
                mission_length = LEAST_MISSION_LENGTH

            mission_offset = 0

            with open(file_name,'r', newline='') as csv_editor:
                all_missions = list(csv.reader(csv_editor))
            print(f"미션 리스트 로딩 완료! ({len(all_missions)}건)")

            # LA 모드: 미션 리스트 사전 분석
            if algo_mode == 'LA':
                print("LA 모드: 미션 리스트 분석 중...")
                _out_count = {}
                for i in range(min(LEAST_MISSION_LENGTH, len(all_missions))):
                    line = all_missions[i]
                    if line[1] == 'OUT':
                        pname = f"{int(line[2]):02d}"
                        _out_count[pname] = _out_count.get(pname, 0) + 1
                _max_freq = max(_out_count.values()) if _out_count else 1
                SPDTw._freq_table = {k: v / _max_freq for k, v in _out_count.items()}
                print(f"  빈도 테이블: {SPDTw._freq_table}")

            _inventory_limit = (
                SPDTw.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name]
                .Area_dict['Area_01'].INVENTORY_CRITICAL_LIMIT
            )

            # 시각화 데이터 수집기 초기화
            _area_01 = SPDTw.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict['Area_01']
            viz = VizCollector(
                seed=seed, algo=algo_mode,
                col=_area_01.COL, row=_area_01.ROW, height=_area_01.HEIGHT,
                total_missions=LEAST_MISSION_LENGTH
            )

            # S 모드: 미션별 상세 로그 유지 / N 모드: 진행률 바만 표시
            _sim_mode = (op_mode == 's')
            if not _sim_mode:
                logger.removeHandler(log_streamer)

            print(f"\n미션 처리 시작 (총 {LEAST_MISSION_LENGTH:,}건, 창고용량: {_inventory_limit})")
            print("=" * 60)
            _progress_step = max(1, LEAST_MISSION_LENGTH // 100)  # 1% 단위
            _start_time = time.time()
            _cnt = {'IN': 0, 'OUT': 0, 'WAIT': 0, 'skip_full': 0, 'skip_empty': 0}

            for _ in range(LEAST_MISSION_LENGTH):

                if not _sim_mode and _ % _progress_step == 0 and _ > 0:
                    _pct = _ * 100 // LEAST_MISSION_LENGTH
                    _elapsed = time.time() - _start_time
                    _eta = _elapsed / _ * (LEAST_MISSION_LENGTH - _)
                    _inv_count = len(SPDTw.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict['Area_01'].inventory)
                    print(
                        f"\r  [{'#' * (_pct // 5):20s}] {_pct:3d}% ({_:,}/{LEAST_MISSION_LENGTH:,}) "
                        f"경과:{_elapsed:.0f}s 남은:{_eta:.0f}s | "
                        f"IN:{_cnt['IN']:,} OUT:{_cnt['OUT']:,} WAIT:{_cnt['WAIT']:,} "
                        f"재고:{_inv_count}/{_inventory_limit} "
                        f"스킵:{_cnt['skip_full']+_cnt['skip_empty']}",
                        end="", flush=True)

                action = product_name = dom = wait_time = None

                line_idx = _ + mission_offset
                if line_idx < len(all_missions):
                    line = all_missions[line_idx]
                    action = line[1]

                    if action in ['IN', 'OUT']:
                        product_name = f"{int(line[2]):02d}"
                        if action == 'IN':
                            dom = line[3]
                    elif action in ['WAIT']:
                        wait_time = line[2]

                # S 모드: 미션 시작 로그
                if _sim_mode:
                    _inv_count = len(SPDTw.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict['Area_01'].inventory)
                    _elapsed = time.time() - _start_time
                    _mission_num = _ + 1 - mission_offset
                    print(f"\n[미션 {_mission_num:,} / {LEAST_MISSION_LENGTH:,}] "
                          f"({action}) 상품:{product_name or '-'} | "
                          f"재고:{_inv_count}/{_inventory_limit} | 경과:{_elapsed:.0f}s")

                if action == 'IN':
                    try:
                        moved_distance, lot = SPDTw.Inbound(product_name=product_name, DOM=dom, testing_mode = True)
                        _cnt['IN'] += 1
                        if _sim_mode:
                            print(f"  -> 입고 완료: {lot} | 이동거리: {moved_distance}")
                        logger.info(f"IN {lot}")
                        sum_distance = [m+s for m,s in zip(moved_distance,sum_distance)]
                        unit_time_past += sum([d*s for d,s in zip(moved_distance, GANTRY_MOVING_SPEED)])
                    except NotEnoughSpaceError:
                        mission_offset += 1
                        _cnt['skip_full'] += 1
                        if _sim_mode:
                            print(f"  -> 스킵: 창고 공간 부족")
                        logger.info("입고 명령 무시 : 창고 공간 부족")
                        logger.warning(f"IN 실패 {product_name} NotEnoughSpaceError")
                        continue
                elif action == 'OUT':
                    try:
                        moved_distance, lot = SPDTw.Outbound(product_name=product_name, testing_mode = 1)
                        _cnt['OUT'] += 1
                        if _sim_mode:
                            print(f"  -> 출고 완료: {lot} | 이동거리: {moved_distance}")
                        logger.info(f"OUT {lot}")
                    except ProductNotExistError:
                        _cnt['skip_empty'] += 1
                        if _sim_mode:
                            print(f"  -> 스킵: 해당 품목 없음")
                        logger.info("출고 명령 무시 : 해당 품목의 상품 없음")
                        logger.warning(f"OUT 실패 {product_name} ProductNotExistError")
                        continue
                    sum_distance = [m+s for m,s in zip(moved_distance,sum_distance)]
                    unit_time_past += sum([d*s for d,s in zip(moved_distance, GANTRY_MOVING_SPEED)])
                elif action == 'WAIT':
                    _cnt['WAIT'] += 1
                    if _sim_mode:
                        print(f"  -> 대기: {wait_time}")

                # 시각화 스냅샷 수집
                viz.collect(
                    mission_num=_,
                    grid=_area_01.grid,
                    product_I_dict=SPDTw.product_I_dict,
                    cum_distance=sum_distance,
                    inv_count=len(_area_01.inventory),
                    counts=_cnt
                )

                if action == 'WAIT':
                    logger.info(
                        f"mission_{_+1-mission_offset} fin (mission list # {_})\n"+
                        f"Waiting time : {wait_time}"+
                        f"Total Unit time past : {unit_time_past}\n"+
                        "-----------------------------------------------------------"+"\n"
                        )
                else:
                    logger.info(
                        f"\nMission_{_+1-mission_offset} fin! fin (mission list # {_})\n"+
                        f"moved_distance : {moved_distance}\n"+
                        f"Unit time past : {sum([d*s for d,s in zip(moved_distance, GANTRY_MOVING_SPEED)])}\n"+
                        f"Total Unit time past : {unit_time_past}\n"+
                        "-----------------------------------------------------------"+"\n"
                        )

            _elapsed = time.time() - _start_time
            _inv_count = len(SPDTw.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict['Area_01'].inventory)
            print(
                f"\r  [{'#' * 20}] 100% ({LEAST_MISSION_LENGTH:,}/{LEAST_MISSION_LENGTH:,}) "
                f"완료! ({_elapsed:.1f}s)"
                f"                                                  ")
            print(
                f"  결과 - IN:{_cnt['IN']:,} | OUT:{_cnt['OUT']:,} | WAIT:{_cnt['WAIT']:,} | "
                f"재고:{_inv_count}/{_inventory_limit} | "
                f"스킵(공간부족):{_cnt['skip_full']} 스킵(상품없음):{_cnt['skip_empty']}")
            print("=" * 60)

            # 터미널 로그 출력 복원 (N 모드에서만 제거했으므로)
            if not _sim_mode:
                logger.addHandler(log_streamer)

            eval_score = Evaluator(mode=op_mode, SEED=seed, mission_length = LEAST_MISSION_LENGTH)
            final_score, time_score, position_score, average_height = eval_score.evaluate(
                time_past=unit_time_past,
                grid_list=SPDTw.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict['Area_01'].grid
                )

            print(f"\n{'=' * 60}")
            print(f"  평가 결과 (SEED={seed:06d})")
            print(f"  {'─' * 40}")
            print(f"  총 이동거리   : [{sum_distance[0]:.1f}, {sum_distance[1]:.1f}]")
            print(f"  총 소요시간   : {unit_time_past:,.1f}")
            print(f"  높이 표준편차 : {average_height:.4f}")
            print(f"  {'─' * 40}")
            print(f"  시간 점수     : {time_score*100:.2f}%")
            print(f"  위치 점수     : {position_score:.2f}")
            print(f"  종합 점수     : {final_score*100:.2f}%")
            print(f"{'=' * 60}")

            logger.info(
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

            # 시각화 HTML 생성
            viz_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "docs", "viz")
            viz_path = viz.generate_html(
                output_dir=viz_dir,
                final_score=final_score,
                time_score=time_score,
                pos_score=position_score
            )
            print(f"\n  시각화 파일 생성: {viz_path}")
            print(f"  브라우저에서 열기: file:///{viz_path}")
            
            # time.sleep(5)


else:
    pass
