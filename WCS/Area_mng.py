import math


class area_manager():
    '''

    리스트 기반 겐트리 창고의 구역 내 물품 추적 및 이동 순서를 관리하는 메니저

    초기화에 구역의 이름:str, 행:float(미터), 열:float(미터), 최대 높이:float(미터), 그리드 형태:str in ['square', 'triangle'], 그리드 사이즈:float(미터) 필요

    '''

    def __init__(self,
                 Area_name:str,
                 origin_point:list,
                 grid_type:str='rectangle',
                 row_block:int=0,
                 col_block:int=0,
                 height_block:int=0,
                 ):
        '''
        구역 그리드 생성
        '''

        self.inventory = {}
        '''
        {
        'lot':{
            'loc' : [x,y,z],

            }
        }
        '''

        self.AREA_NAME = Area_name
        self.GRID_TYPE = grid_type
        self.ORIGIN_POINT = origin_point

        self.COL = col_block
        self.ROW = row_block
        self.HEIGHT = height_block
        # 최대 적재량에서 정렬 불가능한 높이만큼 제외
        self.INVENTORY_CRITICAL_LIMIT   = self.COL * self.ROW * self.HEIGHT - self.HEIGHT + 1
        self.INVENTORY_LIMIT            = self.COL * self.ROW * self.HEIGHT - self.HEIGHT*(self.HEIGHT-1)

        self.grid = []
        for x in range(self.COL):
            self.grid.append([])
            for y in range(self.ROW):
                self.grid[x].append([])
