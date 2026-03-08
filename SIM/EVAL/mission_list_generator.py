import random as rand
import time
import datetime as dt
import sys
from pathlib import Path
import os
import csv
import bisect

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

VERBOSE = '--verbose' in sys.argv or '-v' in sys.argv

if VERBOSE:
    print(sys.argv)
    print(setting)
    print(SEED)

class mission_list_generator():
    action_list = ['IN', 'OUT', 'WAIT']
    item_type_dict = {
        '01': { 'io_f':'HH' },
        '02': { 'io_f':'LL' },
        '03': { 'io_f':'HL' },
        '04': { 'io_f':'HH' },
    }

    def __init__(self, rand_seed = None):
        if rand_seed:
            self.Rand = rand
            self.Rand.seed(rand_seed)

        self.id = 0
        self.last_action = ''
        self.total_items = 0
        # product_id별로 DOM 정렬된 리스트 유지 (bisect 사용)
        self.items_by_product = {pid: [] for pid in self.item_type_dict}
        self._product_id_keys = list(self.item_type_dict.keys())

        self.file_name = f"{os.path.dirname(os.path.realpath(__file__))}/mission_list/mission_list_SEED-{int(str(SEED)):06d}.csv"
        if os.path.isfile(self.file_name):
            os.remove(self.file_name)
        else:
            Path(self.file_name).touch(exist_ok=True)

        iteration = 1
        max_item = 0
        _cnt = {'IN': 0, 'OUT': 0, 'WAIT': 0}
        _progress_step = max(1, MISSION_LIMMIT // 20)  # 5% 단위
        _start_time = time.time()
        _rows_buffer = []

        with open(self.file_name, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)

            while iteration < MISSION_LIMMIT + 1:
                if iteration % _progress_step == 0:
                    _pct = iteration * 100 // MISSION_LIMMIT
                    _elapsed = time.time() - _start_time
                    _eta = _elapsed / iteration * (MISSION_LIMMIT - iteration) if iteration > 0 else 0
                    print(
                        f"\r  [{'#' * (_pct // 5):20s}] {_pct:3d}% ({iteration:,}/{MISSION_LIMMIT:,}) "
                        f"경과:{_elapsed:.0f}s 남은:{_eta:.0f}s | "
                        f"IN:{_cnt['IN']:,} OUT:{_cnt['OUT']:,} WAIT:{_cnt['WAIT']:,} "
                        f"재고:{self.total_items:,}",
                        end="", flush=True)

                val = None
                if self.id == 0:
                    val = self.action_in()
                else:
                    action = self.Rand.choices([self.action_in, self.action_out, self.action_wait],
                                               weights = ACTION_WEIGHTS)[0]
                    if action == self.action_wait and self.last_action == 'WAIT':
                        continue
                    elif action == self.action_out:
                        if self.total_items > 0:
                            available = [pid for pid in self._product_id_keys if self.items_by_product[pid]]
                            val = action(self.Rand.choice(available))
                        else:
                            continue
                    else:
                        val = action()

                if val:
                    _cnt[val['action']] += 1

                row = self._make_row(iteration, val)
                if row:
                    _rows_buffer.append(row)
                if len(_rows_buffer) >= 1000:
                    csv_writer.writerows(_rows_buffer)
                    _rows_buffer.clear()

                iteration += 1
                max_item = max(max_item, self.total_items)

            if _rows_buffer:
                csv_writer.writerows(_rows_buffer)

        _elapsed = time.time() - _start_time
        print(
            f"\r  [{'#' * 20}] 100% ({MISSION_LIMMIT:,}/{MISSION_LIMMIT:,}) 완료! ({_elapsed:.1f}s)"
            f"                                        ")
        print(
            f"  결과 - IN:{_cnt['IN']:,} | OUT:{_cnt['OUT']:,} | WAIT:{_cnt['WAIT']:,} | "
            f"최대 재고:{max_item:,}")


    def action_in(self, product_id = None):
        self.last_action = 'IN'
        self.id += 1

        dom = dt.datetime(2020,1,1) + dt.timedelta(days = self.Rand.randint(0,(dt.datetime(2025,12,12)-dt.datetime(2020,1,1)).days))

        if not product_id:
            product_id = self._product_id_keys[
                self.Rand.choices(range(len(self._product_id_keys)),
                IN_FREQUENCY)[0]
                ]

        io_f = self.item_type_dict[product_id]['io_f']
        new_item = (dom, self.id, product_id, io_f)  # tuple (DOM 기준 정렬용)

        # DOM 순서로 정렬 삽입 → O(log n)
        bisect.insort(self.items_by_product[product_id], new_item)
        self.total_items += 1

        if VERBOSE:
            print(f"IN\tID: {self.id:04d}\tProduct_id: {product_id}")
        return({'action':'IN', 'product_id':product_id, 'dom':dom})


    def action_out(self, product_id = None):
        self.last_action = 'OUT'

        if not product_id:
            product_id = self._product_id_keys[
                self.Rand.choices(range(len(self._product_id_keys)),
                OUT_FREQUENCY)[0]
                ]

        product_items = self.items_by_product[product_id]
        if not product_items:
            return None

        # Oldest_first: 이미 DOM 정렬되어 있으므로 첫 번째가 가장 오래됨 → O(1)
        out_item = product_items.pop(0)
        self.total_items -= 1
        item_id = out_item[1]

        if VERBOSE:
            print(f"OUT\tID: {item_id:04d}\tProduct_id: {product_id}")
        return({'action':'OUT', 'product_id':product_id})


    def action_wait(self):
        self.last_action = 'WAIT'
        wait_time = self.Rand.randint(61,1800)
        if VERBOSE:
            print(f"WAIT\twait_time: {wait_time}")
        return({'action':'WAIT', 'wait_time':wait_time})


    def _make_row(self, iter, action_dict):
        if action_dict == None:
            return None

        if action_dict['action'] == 'WAIT':
            return [iter, action_dict['action'], action_dict['wait_time']]
        elif action_dict['action'] in ['IN', 'OUT']:
            row = [iter, action_dict['action'], action_dict['product_id']]
            if action_dict['action'] == 'IN':
                date = f"{action_dict['dom'].year:04d}{action_dict['dom'].month:02d}{action_dict['dom'].day:02d}"
                row.append(date)
            return row
        return None



if __name__ == '__main__':
    eval = mission_list_generator(rand_seed=SEED)
