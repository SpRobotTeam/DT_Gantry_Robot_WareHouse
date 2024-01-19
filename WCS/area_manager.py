import math
from error import error_code_dict 



class area_manager():
    '''
    
    리스트 기반 겐트리 창고의 구역 내 물품 추적 및 이동 순서를 관리하는 메니저

    초기화에 구역의 이름:str, 행:float(미터), 열:float(미터), 최대 높이:float(미터), 그리드 형태:str in ['square', 'triangle'], 그리드 사이즈:float(미터) 필요

    '''

    

    def __init__(self, area_name:str, row:float, col:float, max_height:float, grid_type:str='square', grid_size:float=1):
        '''
        구역 그리드 생성
        '''
        for i in [row, col, max_height, grid_size]:
            if i >= 0:
                self.error('invalid_input')


        self.grid = temp_list = []
        for j in range(math.floor(col)):
            temp_list.append([])
        for i in range(math.floor(row)):
            self.grid.append(temp_list)
        self.max_height = max_height
        self.grid_type = grid_type

    def read_stock_state(self):
        pass

    def write_stock_state(self, target, state):
        pass

    def find_target(self, target):
        pass

    def put_target(self, target):
        pass

    def pick_target(self, target):
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
        

