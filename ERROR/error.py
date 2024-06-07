class NotEnoughSpaceError(Exception):
    def __init__(self):
        super().__init__('Area에 공간이 충분하지 않습니다.')

class SimError(Exception):
    def __init__(self):
        super().__init__('시뮬레이션 중 에러가 발생했습니다.')

class ProductNotExistError(Exception):
    def __init__(self):
        super().__init__('요청한 제품이 현재 재고 목록에 없습니다.')       

class DB_ObjectNotExistError(Exception):
    def __init__(self):
        super().__init__('요청한 항목이 DB 목록에 없습니다.')  


# error_code_dict = {
#                 'invalid_input' : ['입력이 유효하지 않습니다. 다시 입력해 주세요.'],
                
# }


