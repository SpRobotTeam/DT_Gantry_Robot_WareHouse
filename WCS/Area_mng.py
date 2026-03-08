import math


class TrackedStack(list):
    """grid[x][y] 스택 - append/pop 시 area의 높이 인덱스 자동 업데이트"""
    __slots__ = ('_area', '_x', '_y')

    def __init__(self, area, x, y):
        super().__init__()
        self._area = area
        self._x = x
        self._y = y

    def append(self, item):
        old_h = len(self)
        super().append(item)
        self._area._on_height_change(self._x, self._y, old_h, old_h + 1)

    def pop(self, index=-1):
        old_h = len(self)
        item = super().pop(index)
        self._area._on_height_change(self._x, self._y, old_h, old_h - 1)
        return item


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

        # 높이 인덱스: _positions_by_height[h] = height가 h인 (x,y) 집합
        self._heights = [[0] * self.ROW for _ in range(self.COL)]
        self._positions_by_height = [set() for _ in range(self.HEIGHT)]
        self._min_height = 0

        # 출고구(In/Out)까지의 XY 평면 거리 사전 계산
        ox, oy = self.ORIGIN_POINT[0], self.ORIGIN_POINT[1]
        self._xy_dist = []
        for x in range(self.COL):
            row_dist = []
            for y in range(self.ROW):
                row_dist.append(((x + ox) ** 2 + (y + oy) ** 2) ** 0.5)
            self._xy_dist.append(row_dist)
        self._max_xy_dist = 1.0
        for row_dist in self._xy_dist:
            if row_dist:
                self._max_xy_dist = max(self._max_xy_dist, max(row_dist))

        self.grid = []
        for x in range(self.COL):
            self.grid.append([])
            for y in range(self.ROW):
                self.grid[x].append(TrackedStack(self, x, y))
                if self.HEIGHT > 0:
                    self._positions_by_height[0].add((x, y))

    def _on_height_change(self, x, y, old_h, new_h):
        """grid[x][y]의 높이 변경 시 인덱스 업데이트"""
        if old_h < self.HEIGHT:
            self._positions_by_height[old_h].discard((x, y))
        if new_h < self.HEIGHT:
            self._positions_by_height[new_h].add((x, y))
        self._heights[x][y] = new_h
        if new_h < self._min_height:
            self._min_height = new_h
        elif old_h == self._min_height and old_h < self.HEIGHT and not self._positions_by_height[old_h]:
            for h in range(old_h + 1, self.HEIGHT):
                if self._positions_by_height[h]:
                    self._min_height = h
                    break
            else:
                self._min_height = self.HEIGHT
