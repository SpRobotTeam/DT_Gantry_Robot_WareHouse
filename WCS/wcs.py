import WCS.Info_manager as Info_manager

class GantryWCS ():
    def __init__(self):
        self.base_info = Info_manager.base_info()

    def __init__(self, saved_file):
        self.base_info = Info_manager.base_info(saved_file)

    def Inbound(self, I_id):
        pass
        if not I_id in self.base_info.Product_list:
            # 입력 리스트
            # 제품 ID
            # 기본 LOT 넘버
            # 생산 속성 (생산 주기)
            # 시장 속성 (이동 주기)
            # 고유 특성 (위험 요소 또는 )
            # 적재 규칙 #?
            self.base_info.Product_list.append()
        # area_manager
        # PLC_com ()
        

    def Outbound(self, I_id):
        pass

    