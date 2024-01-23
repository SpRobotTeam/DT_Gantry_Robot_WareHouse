import WCS.Area_mng as Area_mng
import PLC_com

class zone_manager():
    # plc_server = PLC_com.server()
    # plc_client = PLC_com.client()
    Modbus_inst = PLC_com.plc_com()

    # mission_enabled = False
    Area_list = []
    def __init__(self, 
                 container, 
                 area_length = None,
                 area_width = None,
                 area_height = None
                 ):
        
        if not area_length:
            area_length = 12000
        if not area_width:
            area_width  = 7000
        if not area_height:
            area_height = 1600

        self.col_total = area_length//container['length'] # 34
        self.row_total = area_width//container['width'] # 31        
        self.heigth_total = area_height//container['heigth'] # 8
        
        
        self.Gantry    = Area_mng.area_manager(area_name="temp",   
                                                    # origin_point=[0,30], 
                                                    col_block=1,  
                                                    row_block=1 , 
                                                    height_block=self.heigth_total, 
                                                    grid_type='r'
                                                    )
        self.Area_list.append('Gantry')
        self.In      = Area_mng.area_manager(area_name="In",     
                                                    origin_point=[0,self.row_total,0],  
                                                    col_block=1,  
                                                    row_block=1, 
                                                    height_block=self.heigth_total, 
                                                    grid_type='r'
                                                    )
        self.Area_list.append('In')
        self.Out     = Area_mng.area_manager(area_name="Out",    
                                                    origin_point=[0,0,0], 
                                                    col_block=1,  
                                                    row_block=1, 
                                                    height_block=self.heigth_total, 
                                                    grid_type='r'
                                                    )
        self.Area_list.append('Out')
        A01 = Area_mng.area_manager(area_name="Area_01",
                                                    origin_point=[1,0,0],  
                                                    col_block=self.col_total-1, 
                                                    row_block=self.row_total, 
                                                    height_block=self.heigth_total, 
                                                    # row=container['width'],
                                                    # col=container['length'],
                                                    # height=container['height'],
                                                    grid_type='r'
                                                    )
        self.Area_list.append('A01')
    
    # def add_area(self, area_name, container):
    #     self.exec()
        
    #     Area_name = Area_mng.area_manager(area_name="Area_01",
    #                                                 origin_point=[1,0,0],  
    #                                                 col_block=col_total-1, 
    #                                                 row_block=row_total, 
    #                                                 height_block=heigth_total, 
    #                                                 # row=container['width'],
    #                                                 # col=container['length'],
    #                                                 # height=container['height'],
    #                                                 grid_type='r'
    #                                                 )

    
    def outbound(self, loc:list):
        set_list = [1] + loc + [1] + self.Out.origin_point + [2]
        # self.plc_client.write(address=0, set_list=set_list)


    def inbound(self, loc):
        pass

    
    def read_stock_state(self)->list:
        pass


    def write_stock_state(self, target, state):
        pass

    
    # def find_loc (self, target) -> list[int,int,int]:
    #     '''
    #     타겟 위치(정수 col,row,height)를 출력하는 합수
    #     '''
    #     # for i in range(self.col):
    #     #     for j in range(self.row):
    #     #         for k in range(self.height):
    #     #             if self.grid[i][j][k] == target:
    #     #                 return [i,j,k]


    
    def sort(slef,):
        pass
    

    def arrange(self,):
        pass

