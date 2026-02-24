import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from WCS.Info_mng import Base_info


class GantryWCS (Base_info):
    def __init__(self, op_mode = None):
        Base_info.__init__(self, op_mode=op_mode)


if __name__ == '__main__':
    print(
        "이 프로그램은 직접 실행 할 수 없습니다. ",
        "이 모듈을 다른 프로그램에서 불러와서 사용하세요."
          )
