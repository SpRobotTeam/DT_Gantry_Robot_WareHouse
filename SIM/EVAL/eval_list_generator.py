import random as rand
import time 
import datetime as dt
import sys
from pathlib import Path
import os
import csv

class eval_list_generator():
    action_list = ['IN', 'OUT', 'WAIT']
    item_list = []
    id = 0
    last_action = ''
    # item_templet = {
    #     'item_id'               : 0,
    #     'product_id'            : '00',
    #     'date_of_manufacture'   : '000000',
    #     'I/O_frequency'         : 'LL',
    # }
    item_type_dict = {
        '01': {
            'io_f':'HH',
            },
        '02': {
            'io_f':'LL',
            },
        '03': {
            'io_f':'HL',
            },
        '04': {
            'io_f':'HH',
            },
    }

    def __init__(self, rand_seed = None):
        if rand_seed:
            self.Rand = rand
            self.Rand.seed(rand_seed)

        self.file_name = f"{os.path.dirname(os.path.realpath(__file__))}/eval_list.csv"
        try:
            os.remove(self.file_name)
        except:
            pass
        Path(self.file_name).touch(exist_ok=True)
        
        iteration = 1
        # for iteration in range(100):
        while iteration < 100 +1 :
            print(f"iter : {iteration}")
            val = None
            if self.id == 0:
                val = self.action_in()
                # self.write(iteration, self.action_in())
            else:
                action = self.Rand.choice([self.action_in, self.action_out, self.action_wait])
                if action == self.action_wait and self.last_action == 'WAIT':
                    # iteration -= 1
                    continue
                elif action == self.action_out:
                    if len(self.item_list):
                        product_id_list = []
                        for item in self.item_list:
                            if not item['product_id'] in product_id_list:
                                product_id_list.append(item['product_id'])
                        
                        val = action(self.Rand.choice(product_id_list))
                    else :
                        continue
                    #     iteration -= 1
                else:
                    # action()
                    val = action()
                    # self.write(iteration, action())
            self.write(iteration, val)
            iteration += 1
            


    def action_in(self, product_id = None):
        self.last_action = 'IN'
        self.id += 1
        
        # new_item = self.item_templet
        
        dom = dt.datetime(2020,1,1) + dt.timedelta(days = self.Rand.randint(0,(dt.datetime(2025,12,12)-dt.datetime(2020,1,1)).days))
        
        if not product_id:
            product_id = self.Rand.choice(list(self.item_type_dict.keys()))

        io_f = self.item_type_dict[product_id]['io_f']
        # new_item.update(
        new_item = \
            {
                'item_id'               : self.id,
                'product_id'            : product_id,
                'date_of_manufacture'   : dom,
                'I/O_frequency'         : io_f,
            }
        # )
        self.item_list.append(new_item)
        
        print(f"IN\tID: {self.id:04d}\tProduct_id: {product_id}") #d
        return({'action':'IN', 'product_id':product_id, 'dom':dom})


    def action_out(self, product_id = None):
        self.last_action = 'OUT'

        if not product_id:
            product_id = self.Rand.choice(self.item_type_dict.keys())
        
        out_item_list = []
        for i in self.item_list:
            if i['product_id'] == product_id:
                out_item_list.append(i)

        # 랜덤
        # out_item = self.Rand.choice(out_item_list) #random_out
        # FIFO
        # out_item = out_item_list[0] #FIFO_out
        # Oldest_first
        out_item_dict=dict(zip(                                                 #oldest_first_out
            [i['item_id'] for i in out_item_list],                              #oldest_first_out
            # [i['date_of_manufacture'] for i in out_item_list],                  #oldest_first_out
            [i for i in out_item_list]))                                        #oldest_first_out
        out_item_list_sorted = sorted(                                          #oldest_first_out
            out_item_dict.items(),                                              #oldest_first_out
            key=lambda item:item[1]['date_of_manufacture'])                     #oldest_first_out
        out_item = out_item_list_sorted[0][-1]                                  #oldest_first_out
        
        id = out_item['item_id']                                                

        print(f"OUT\tID: {id:04d}\tProduct_id: {product_id}")
        self.item_list.remove(out_item)
        return({'action':'OUT', 'product_id':product_id})
        

    def action_wait(self):
        self.last_action = 'WAIT'
        wait_time = self.Rand.randint(61,1800)
        print(f"WAIT\twait_time: {wait_time}")
        return({'action':'WAIT', 'wait_time':wait_time})


    def write(self, iter,
            #   action:str = None, product_id:str = None, dom:dt.datetime = None, io_f:str = None, wait_time:int = None
              action_dict:dict
              ):
        
        if action_dict == None:
            print("error, trying again") #d
            return(0)

    
        else:
            if action_dict['action'] == 'WAIT':
                print(f"recived:\taction: {action_dict['action']}, \twait_time: {action_dict['wait_time']}")
                write_list = [action_dict['wait_time']]
            elif action_dict['action'] in ['IN', 'OUT']:
                print(f"recived:\taction: {action_dict['action']}, \tProduct_id: {action_dict['product_id']}")
                write_list = [action_dict['product_id']]
                if action_dict['action'] == 'IN':
                    date = str(action_dict['dom'].year)[-2:]+str(action_dict['dom'].month)+str(action_dict['dom'].day)
                    write_list.append(date)
        print(f"current item list : {[[i['item_id'],i['product_id']] for i in self.item_list]}\n")
        with open(self.file_name,'a+', newline='') as csv_editor:
            csv_appender = csv.writer(csv_editor)
            csv_appender.writerow([iter, action_dict['action']]+write_list)



if __name__ == '__main__':
    eval = eval_list_generator(rand_seed=8291)
    
