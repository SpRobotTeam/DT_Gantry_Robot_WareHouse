import random as rand
import time 
import datetime as dt
import sys
from pathlib import Path
import os
import csv

SEED = 12345
MISSION_LIMMIT = 1000
ACTION_WEIGHTS = [0.5, 0.3, 0.2]
IN_FREQUENCY  = [1,1,1,1] # [5, 1, 3, 4]
OUT_FREQUENCY = [1,1,1,1] # [5, 1, 2, 4]

setting = ['', SEED, MISSION_LIMMIT, *ACTION_WEIGHTS]

if len(sys.argv) >= 2:
    for i in range(len(sys.argv)):
        if i == 0:
            setting[i] = sys.argv[i]
        else:
            setting[i] = float(sys.argv[i])

_, SEED, MISSION_LIMMIT = setting[:3]
SEED = int(SEED)
MISSION_LIMMIT = int(MISSION_LIMMIT)
ACTION_WEIGHTS = setting[3:]

if __name__ == '__main__':
    print(sys.argv)
    print(setting)
    print(SEED)

class mission_list_generator():
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

        # self.file_name = f"{os.path.dirname(os.path.realpath(__file__))}/mission_list/mission_list_SEED-{SEED:06d}.csv"
        self.file_name = f"{os.path.dirname(os.path.realpath(__file__))}/mission_list/mission_list_SEED-{int(str(SEED)):06d}.csv"
        if os.path.isfile(self.file_name):
            os.remove(self.file_name)
        else:
            Path(self.file_name).touch(exist_ok=True)
        
        iteration = 1
        # for iteration in range(100):
        max_item = 0

        while iteration < MISSION_LIMMIT +1 :
            if __name__ == '__main__':
                print(f"iter : {iteration}")
            val = None
            if self.id == 0:
                val = self.action_in()
                # self.write(iteration, self.action_in())
            else:
                action = self.Rand.choices([self.action_in, self.action_out, self.action_wait],
                                           weights = ACTION_WEIGHTS)[0]
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
            max_item = max(max_item, len(self.item_list))
        if __name__ == '__main__':
            print(
                f"Max amount of items :\t{max_item}\n" # +
                # f""
                    )
            


    def action_in(self, product_id = None):
        self.last_action = 'IN'
        self.id += 1
        
        # new_item = self.item_templet
        
        dom = dt.datetime(2020,1,1) + dt.timedelta(days = self.Rand.randint(0,(dt.datetime(2025,12,12)-dt.datetime(2020,1,1)).days))
        
        if not product_id:
            product_id = list(self.item_type_dict.keys())[
                self.Rand.choices(range(len(self.item_type_dict.keys())), 
                IN_FREQUENCY)[0]
                ]

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
        
        if __name__ == '__main__':
            print(f"IN\tID: {self.id:04d}\tProduct_id: {product_id}") #d
        return({'action':'IN', 'product_id':product_id, 'dom':dom})


    def action_out(self, product_id = None):
        self.last_action = 'OUT'

        if not product_id:
            product_id = list(self.item_type_dict.keys())[
                self.Rand.choices(range(len(self.item_type_dict.keys())), 
                IN_FREQUENCY)
                ]
        
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

        if __name__ == '__main__':
            print(f"OUT\tID: {id:04d}\tProduct_id: {product_id}")
            self.item_list.remove(out_item)
        return({'action':'OUT', 'product_id':product_id})
        

    def action_wait(self):
        self.last_action = 'WAIT'
        wait_time = self.Rand.randint(61,1800)
        if __name__ == '__main__':
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
                if __name__ == '__main__':
                    print(f"recived:\taction: {action_dict['action']}, \twait_time: {action_dict['wait_time']}")
                write_list = [action_dict['wait_time']]
            elif action_dict['action'] in ['IN', 'OUT']:
                if __name__ == '__main__':
                    print(f"recived:\taction: {action_dict['action']}, \tProduct_id: {action_dict['product_id']}")
                write_list = [action_dict['product_id']]
                if action_dict['action'] == 'IN':
                    # date = str(action_dict['dom'].year)[-2:]+str(action_dict['dom'].month)+str(action_dict['dom'].day)
                    date = f"{action_dict['dom'].year:04d}{action_dict['dom'].month:02d}{action_dict['dom'].day:02d}"
                    write_list.append(date)
        if __name__ == '__main__':
            print(f"current item list (amount : {len(self.item_list)}) : \n{[[i['item_id'],i['product_id']] for i in self.item_list]}\n")
        with open(self.file_name,'a+', newline='') as csv_editor:
            csv_appender = csv.writer(csv_editor)
            csv_appender.writerow([iter, action_dict['action']]+write_list)



if __name__ == '__main__':
    eval = mission_list_generator(rand_seed=SEED)
    
