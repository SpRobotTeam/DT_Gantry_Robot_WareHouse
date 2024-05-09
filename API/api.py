from odoo_api_wrapper import odoo_xmlrpc

class SPDT_API():
    object_dict = {    
    'ware_house' : "stock.warehouse",
    'zone' : "stock.location", #?
    'area' : "stock.loaction", #?
    'product_templet' : "product.templet",
    'container' : "product.container", #?
    'product_product' : "product.product",
    'history' : "stock.",
    'stock_move' : "stock.move",
    'schedule' : "stock.",
    }
    def __init__(self, username=None, password=None, api_key=None):
        self.odoo_api = odoo_xmlrpc(username=username, password=password, api_key=api_key)


    def login(self, username=None, password=None, api_key=None):
        return self.odoo_api.login()
            

# if __name__ == '__main__':
#     test = odoo_xmlrpc()
#     # test.create_data(obj='product.product', args=[])
#     test.login()
#     import pprint

#     # ['stock_quant']
#     table_name = 'stock.picking' # 'stock.location'
#     # args=[{'name' : 'loc_format', }]
#     inst_name = table_name.split('.')[-1]+'_template'
#     test.create_data(obj=table_name, 
#                     # args=[[['type', '=', 'product']]],
#                     args=[{'name' : inst_name, }], 
#                     )
    
#     data = test.search_data(obj=table_name, 
#                     # args=[[['type', '=', 'product']]],
#                     args=[[['name', '=', inst_name]]],
#                     # kw={'fields':['name', 'id', ]}
#                     kw={}
#                     )
#     sorted_data = sorted(data, key=lambda x:(x['name']))
#     pprint.pprint(sorted_data)
#     print([x for x in sorted_data if ' ' in x['name']])
    
        

