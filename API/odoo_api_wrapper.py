import xmlrpc.client



class odoo_xmlrpc():
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
    


    def list_up_records(self, obj:str, args:list, kw=None):
        data = self.__models.execute_kw(self.__db, self.__uid, self.__key, obj, 'search', args, kw)
        return data
    


    def create_data(self, obj:str, args:list):
        '''
        `obj`  : 테이블 이름,
        `args` : 데이터 속성(내용)

        ex)
        create_data('res.partner', [{'name': "New Partner"}])
        '''
        # data = 
        self.__models.execute_kw(self.__db, self.__uid, self.__key, obj, 'create', args)
        # return data



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
        search_data('res.partner', [[['id', '=', id], ]],)
        '''
        # data = 
        self.__models.execute_kw(self.__db, self.__uid, self.__key, obj, 'unlink', args)
        # return data



if __name__ == '__main__':
    test = odoo_xmlrpc()
    # test.create_data(obj='product.product', args=[])
    test.login()
    import pprint
    # test.create_data(obj='product.template',
    #                  args=[{'name':'test03', }]
    #                  )

    data = test.search_data(obj='product.template', 
                            # args=[[['type', '=', 'product']]],
                            args=[[['write_uid', '=', 2]]], 
                            kw={'fields':['name', 'id', ]}
                            )
    sorted_data = sorted(data, key=lambda x:(x['name']))
    pprint.pprint(sorted_data)
    print([x for x in sorted_data if ' ' in x['name']])