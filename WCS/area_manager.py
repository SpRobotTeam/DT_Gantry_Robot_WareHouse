import math
from error import error_code_dict 
import numpy as np



class area_manager():
    '''
    
    리스트 기반 겐트리 창고의 구역 내 물품 추적 및 이동 순서를 관리하는 메니저

    초기화에 구역의 이름:str, 행:float(미터), 열:float(미터), 최대 높이:float(미터), 그리드 형태:str in ['square', 'triangle'], 그리드 사이즈:float(미터) 필요

    '''

    # def __init__(self):
    #     self.area_name = 'Area_01'
    #     self.row = 7000 // (200+20)
    #     self.col = 12000 // (300+20)
    #     self.width = 1600 // 200
        

    def __init__(self, area_name:str, origin_point:list[int,int], row_block:int=0, col_block:int=0, height_block:int=0, row:float=0, col:float=0, height:float=0, grid_size:list[float]=[300,200,200], grid_type:str='rectangle'):
        '''
        구역 그리드 생성
        '''
        grid_set_num = 0
        for j in [[row_block, col_block, height_block], [row, col, height, grid_size]]:
            for i in j:
                if i <= 0:
                    grid_set_num+=1
                    break
                elif  len(j) == j.index(i):
                    break
        if grid_set_num >= 2:
            self.error('invalid_input')

        elif grid_set_num == 0:
            col = col_block
            row = row_block
            height = height_block

        elif grid_type[0].lower() == 'r':
            col = math.floor(col/grid_size[0])
            row = math.floor(row/grid_size[1])
            height = math.floor(height/grid_size[2])
            
        # self.grid = []
        # for j in range(col):
        #     temp_list = []
        #     for i in range(row):
        #         temp_list.append([])
        #     self.grid.append(temp_list)

        self.area_name = area_name
        self.grid_type = grid_type
        self.origin_point = origin_point

        self.grid = np.zeros(col,row,height)

    def read_stock_state(self)->list:
        pass

    def write_stock_state(self, target, state):
        pass

    def find_target(self, target)->list:
        pass

    def put_target(self, target):
        pass

    def pick_target(self, target):
        pass

    def sort(slef,):
        pass
    
    def arrange(self,):
        pass

    def error(self, error_code, *messages):
        # print(f'오류가 발생했습니다.\n')
        for i in error_code_dict[error_code]:
            print(i)
        if messages:
            print("문제가 발생한 변수는 다음과 같습니다 :")
            for i in messages:
                print(i)
        raise(error_code)
        

