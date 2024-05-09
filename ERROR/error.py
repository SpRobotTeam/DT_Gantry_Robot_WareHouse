class NotEnoughSpaceError(Exception):
    def __init__(self):
        super().__init__('Area에 공간이 충분하지 않습니다.')


# error_code_dict = {
#                 'invalid_input' : ['입력이 유효하지 않습니다. 다시 입력해 주세요.'],
                
# }


