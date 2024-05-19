import os
import csv
import pathlib
import numpy as np

class Evaluator():
    
    
    def __init__(self, SEED, standard_time:float = 1000*60*5.0, score_weight:list=[0.7, 0.3], mode=1):
        self.SEED = SEED
        self.file_name = f"{os.path.dirname(os.path.realpath(__file__))}/eval_list/eval_list_SEED-{SEED:06d}.csv"
        
        standard_found = False
        if os.path.isfile(self.file_name):
            with open(self.file_name,'r', newline='') as csv_editor:
                    line_index = 0
                    mission_list = csv.reader(csv_editor)
                    for line in mission_list:
                        name = line[0]
                        if name == 'standard':
                            standard_found = True
                            self.standard_time = float(line[2])
        if not standard_found:
            self.standard_time = standard_time
        self.score_weight = score_weight
        self.mode=mode
        
    
    def evaluate(self, time_past:int, grid_list:list)->list:
        self.time_past = time_past
        self.score = [
            self.time_eval(self.time_past),
            *self.position_eval(grid_list)
        ]
        final_score = sum([s*w for s,w in zip(self.score, self.score_weight)])
        
        pathlib.Path(self.file_name).touch()

        edit_line = 0
        origin = []

        with open(self.file_name,'r', newline='') as csv_editor:
                    line_index = 0
                    mission_list = csv.reader(csv_editor)
                    for line in mission_list:
                        if len(line):
                            name = line[0]
                            if name == 'standard' if self.mode == 1 else self.mode:
                                origin.append(line)
                                edit_line = line_index
                            else:
                                origin.append(line)
                                line_index += 1
                        else:
                             break
        

        
        with open(self.file_name,'w+', newline='') as csv_editor:
            csv_appender = csv.writer(csv_editor)
            if edit_line == 0:
                csv_appender.writerow(['standard' if self.mode == 1 else self.mode, final_score, self.time_past, *self.score])
            else:
                for line in origin:
                    if line == edit_line:
                        csv_appender.writerow(['standard' if self.mode == 1 else self.mode, final_score, self.time_past, *self.score])
                    else: 
                        csv_appender.writerow(origin[line])

        return [final_score, *self.score]


    def time_eval(self, time_past):
        time_score = 1 - (time_past/self.standard_time)

        return time_score
    
    def position_eval(self, grid_list:list):
        height_list = []
        # height_list = [len(grid_list[x][y]) for y in range(len(grid_list[x])) for x in range(len(grid_list))]
        for x in range(len(grid_list)):
            for y in range(len(grid_list[x])):
                height_list.append(len(grid_list[x][y]))

        average_height = np.mean(height_list) # sum(height_list)/len(height_list)

        std = np.std(height_list)
        position_score = 1/std # 1/(average_height)
        
        return [position_score, std]
