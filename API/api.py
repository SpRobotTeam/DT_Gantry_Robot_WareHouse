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
            
    
        

