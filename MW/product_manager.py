
container = {
    'defalut':{
        'width'     : 300, 
        'length'    : 200, 
        'height'    : 200,
        'gap'       : 200
},

}



class product():
    
    def __init__(self, product_id:str, product_name:str, flameable:bool, delicate:bool, container=container['defalut'], combination_indices:list=[], weight=None, inbound_peequency=None, outbound_peequency=None):
        pass