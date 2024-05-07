import xmlrpc.client



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
    
        self.__url      = url if url else 'http://127.0.0.1:8069'
        self.__db       = db if db else 'mydb'
        self.__username = username if username else 'admin'
        self.__password = password if password else None
        self.__api_key  = api_key if api_key else '8e31c53904665a770c6ce58d44bcb86f4db7bb01'
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
            print("로그인 과정에서 오류가 발생하였습니다. 에러:{e}")
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


    # def edit_company(method:str, args=None):
    #     obj = 'res.company'
        
    #     return_val = ''
    #     return return_val

    # def edit_warehouse(method:str, args=None):
    #     obj = 'stock.warehouse'
        
    #     return_val = ''
    #     return return_val

    # def edit_location(method:str, args=None):
    #     obj = 'stock_location'
        
    #     return_val = ''
    #     return return_val

    # def edit_templet(method:str, args=None):
    #     obj = 'product.template'
        
    #     return_val = ''
    #     return return_val

    # def edit_product(method:str, args=None):
    #     obj = 'product.product'
        
    #     return_val = ''
    #     return return_val

    # def edit_quant(method:str, args=None):
    #     obj = 'stock.quantity'
        
    #     return_val = ''
    #     return return_val


    # def edit_lot(method:str, args=None):
    #     obj = 'stock.lot'
        
    #     return_val = ''
    #     return return_val

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