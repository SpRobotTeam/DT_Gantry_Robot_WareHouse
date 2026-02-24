import os
import xmlrpc.client
from ERROR.error import DB_ObjectNotExistError


class odoo_xmlrpc():
    templet_format = {
  
        # 'name': 'test_05',
        'detailed_type': 'product',
        'type': 'product',
        'responsible_id': [2, 'Mitchell Admin'],
        'volume': 0.0,
        'volume_uom_name': 'm³',
        'weight': 0.0,
        'weight_uom_name': 'kg',
        
            }
    
    loaction_format = {
        
        # 'child_ids': [],
        # 'child_internal_location_ids': [49],
        'comment': False,
        'company_id': [3, 'DT'],
        'complete_name': 'loc_format',
        'create_uid': [2, 'Mitchell Admin'],
        'cyclic_inventory_frequency': 0,
        # 'id': 49,
        # 'incoming_move_line_ids': [],
        # 'last_inventory_date': False,
        # 'location_id': False,
        'name': 'loc_format',
        # 'net_weight': 0.0,
        'next_inventory_date': False,
        # 'outgoing_move_line_ids': [],
        # 'parent_path': '49/',
        'posx': 0,
        'posy': 0,
        'posz': 0,
        'putaway_rule_ids': [],
        'quant_ids': [],
        'removal_strategy_id': False,
        # 'replenish_location': False,
        # 'return_location': False,
        # 'scrap_location': False,
        # 'storage_category_id': False,
        # 'usage': 'internal',
        # 'warehouse_id': False,
        # 'warehouse_view_ids': [],
        'write_uid': [2, 'Mitchell Admin']
        }
    

    





    def __init__(self, url=None, db=None, username=None, password=None, api_key=None):

        self.__url      = url or os.environ.get('ODOO_URL', 'http://127.0.0.1:28069')
        self.__db       = db or os.environ.get('ODOO_DB', 'SPDT_DB')
        self.__username = username or os.environ.get('ODOO_USERNAME', '')
        self.__password = password or os.environ.get('ODOO_PASSWORD', '')
        self.__api_key  = api_key or os.environ.get('ODOO_API_KEY', '')
        self.__key      = self.__password if self.__password else self.__api_key



    def login(self):
        try:
            self.__common = xmlrpc.client.ServerProxy(f'{self.__url}/xmlrpc/2/common')
            self.__uid = self.__common.authenticate(self.__db, self.__username, self.__key, {})

            if self.__uid:
                print("Authenticatinon Success") #d
                self.__models = xmlrpc.client.ServerProxy(f'{self.__url}/xmlrpc/2/object')
                return None
        except Exception as e:
            print(f"로그인 과정에서 오류가 발생하였습니다. 에러:{e}")
            return e
    


    def list_up_records(self, obj:str, args:list, kw:dict=None)-> list:
        '''
        조건에 부합하는 레코드(id) 리스트 출력
        `obj`  : 테이블 이름,
        `args` : 데이터 속성(조건)
        `kw`   : 필터

        ex)
        list_up_records('res.partner', [[['is_company', '=', True]]])                           -> [1,2,3,5,10,21,22,23]
        list_up_records('res.partner', [[['is_company', '=', True]]],{'offset': 4, 'limit': 3}) -> [10,21,22]
        '''
        data = self.__models.execute_kw(self.__db, self.__uid, self.__key, obj, 'search', args, kw)
        return data
    


    def create_data(self, obj:str, args:list):
        '''
        레코드 생성
        `obj`  : 테이블 이름,
        `args` : 데이터 속성(내용)

        ex)
        create_data('res.partner', [{'name': "New Partner"}])
        '''
        # data = 
        self.__models.execute_kw(self.__db, self.__uid, self.__key, obj, 'create', args)
        return None



    def list_up_record_filds(self, obj:str, args:list, kw=None):
        '''
        `obj`  : 테이블 이름,
        `args` : 데이터 속성(내용)
        `kw`   : 필터

        ex)
        list_up_record_filds('res.partner', [], {'attributes': ['string', 'help', 'type']})
        '''
        data = self.__models.execute_kw(self.__db, self.__uid, self.__key, obj, 'fields_get', args, kw)
        return data
    

    
    def search_data(self, obj:str, args:list, kw=None):
        '''
        `obj`  : 테이블 이름,
        `args` : 데이터 속성(내용)
        `kw`   : 필터

        ex)
        search_data('res.partner', [[['is_company', '=', True]]], {'offset': 10, 'limit': 5})
        '''

        data = self.__models.execute_kw(self.__db, self.__uid, self.__key, 
                                        obj, 'search_read', args, kw
                                        )
        return data



    def read_data(self, obj:str, args:list, kw=None):
        '''
        `obj`  : 테이블 이름,
        `args` : 데이터 속성(내용)
        `kw`   : 필터

        ex)
        read_data('res.partner', [[['is_company', '=', True]]], {'offset': 10, 'limit': 5})
        '''
        # print(self.__models.execute_kw(__db, uid, __key, 'product.product', 'read',[37]))
        # print(self.__models.execute_kw(self.__db, self.__uid, self.__key, 'product.product', 'read',
        #                         [[37, 1]],
        #                         {'fields':['product_tmpl_id', 'product_template_variant_value_ids', 'free_qty']}))

        data = self.__models.execute_kw(self.__db, self.__uid, self.__key, obj, 'read', args, kw)
        return data



    def update_data(self, obj:str, args:list):
        '''
        `obj`  : 테이블 이름,
        `args` : 데이터 속성(내용)

        ex)
        update_data('res.partner', [[id, ], {'name' : "Newer partner", }])
        '''
        data = self.__models.execute_kw(self.__db, self.__uid, self.__key, obj, 'write', args)
        return data



    def delete_data(self, obj:str, args:list):
        '''
        `obj`  : 테이블 이름,
        `args` : 데이터 속성(내용)

        ex)
        delete_data('res.partner', [[['id', '=', id], ]],)
        '''
        # data = 
        self.__models.execute_kw(self.__db, self.__uid, self.__key, obj, 'unlink', args)
        return None


    def db_wrapper(self, obj:str, method:str, args = None, kw = None):
        data = self.list_up_record_filds(obj=obj, args=args, kw=kw)
        if method == 'read' or args in data:
            pass
        
        else:
            if method == 'create' or args not in data:
                pass

            else:
                for _ in args:
                    for i in _:
                        if type(i) == dict:
                            method = 'write'
                        else:
                            method = 'unlink'
                if method == 'write':
                    pass

                elif method == 'unlink':
                    pass


class SPDT_API():
    object_dict = {    
    'ware_house' : "stock.warehouse",       # 창고 (공간 대분류)
    'zone' : "stock.location",              # 장소 (공간 중분류)
    'area' : "stock.loaction",              # 구역 (공간 소분류)
    'product_templet' : "product.templet",  # 품종 정보
    'container' : "product.container",      # 상품 컨테이너 정보
    'product_product' : "product.product",  # 상품 목록
    'partner' : "res.partner",              # 고객/공급자 정보
    'company' : "res.company",              # 거래 회사 정보
    'stock_move' : "stock.move",            # 상품 이동 명령
    'history' : "stock.move.line",          # 이동 내역
    'schedule' : "stock.",                  # 상품 이동 스케쥴
    }
    def __init__(self, username=None, password=None, api_key=None):
        self.odoo_api = odoo_xmlrpc(username=username, password=password, api_key=api_key)


    def login(self, username=None, password=None, api_key=None):
        return self.odoo_api.login()
    


    def connector(self, object:str, args:list=None, kw=None):
        self.login()

        if object in self.object_dict.keys():
            obj = self.object_dict[object]
        else:
            raise DB_ObjectNotExistError
        
        if not kw==None:
            return self.odoo_api.list_up_records(obj=object, args=args, kw=kw)

        elif 'delete' in args.keys() and args['delete'] == True:
            method = self.odoo_api.delete_data

        elif args['id'] in self.odoo_api.list_up_records:
            method = self.odoo_api.update_data

        else :
            method = self.odoo_api.create_data

        return method(obj=obj, args=args)
    

if __name__ == '__main__':
    test = odoo_xmlrpc()
    # test.create_data(obj='product.product', args=[])
    test.login()
    import pprint

    # ['stock_quant']
    table_name = 'stock.picking' # 'stock.location'
    # args=[{'name' : 'loc_format', }]
    inst_name = table_name.split('.')[-1]+'_template'
    test.create_data(obj=table_name, 
                    # args=[[['type', '=', 'product']]],
                    args=[{'name' : inst_name, }], 
                    )
    
    data = test.search_data(obj=table_name, 
                    # args=[[['type', '=', 'product']]],
                    args=[[['name', '=', inst_name]]],
                    # kw={'fields':['name', 'id', ]}
                    kw={}
                    )
    sorted_data = sorted(data, key=lambda x:(x['name']))
    pprint.pprint(sorted_data)
    print([x for x in sorted_data if ' ' in x['name']])

