#!/bin/python
import sys, os, pathlib
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
current_working_directory = os.getcwd()

from pyModbusTCP.server import ModbusServer, DataBank

from robodk import robolink
from robodk import robomath
from robodk import *
from robolink import *
# import add_model
from time import sleep
import subprocess
home_path = os.path.expanduser('~')

import logging
logger = logging.getLogger('plc_motion006')
logger.setLevel(logging.WARNING)

pathlib.Path("./logs/'plc_motion006'.log").touch
log_file_handler = logging.FileHandler(f"./logs/'plc_motion006'.log", mode="w+")

logger.addHandler(log_file_handler)

logger.info("______________________________________________________________________\nProgram start")

if not 'nt' in os.name:
    subprocess.Popen(["sh", home_path+"/RoboDK/RoboDK-Start.sh"])
    time.sleep(10)

RDK = robolink.Robolink()
if 'nt' in os.name:
    # RDK.AddFile(os.path.dirname(__file__)+"\\"+"wcs_plc_20240203_183935.rdk")
    RDK.AddFile(os.path.dirname(__file__)+"\\"+"wcs_plc_20240508_133800.rdk")
    # RDK.AddFile(os.path.dirname(__file__)+"\\"+"wcs_plc_20240513_133800.rdk")
else:
    RDK.AddFile(os.path.dirname(__file__)+"/"+"wcs_plc_20240508_133800.rdk")
# station_item = RDK.AddFile("wcs_plc_20240508_133800.rdk")
# station = RDK.Item(station_item.Name())
# station.setName("station")

from threading import Thread
########################################################### robodk cam stream
import socket
import numpy
import cv2

UDP_IP = "127.0.0.1"
UDP_PORT = 9505

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

robolink.import_install('cv2', 'opencv-python', RDK)
robolink.import_install('numpy', RDK)
import numpy as np
import cv2 as cv

CAM_NAME = "Camera 1"
CAM_PARAMS = 'SIZE=640x480'
# WINDOW_NAME = CAM_NAME

def camera_stream():
    cam_item = RDK.Item(CAM_NAME, robolink.ITEM_TYPE_CAMERA)
    if not cam_item.Valid():
        cam_item = RDK.Cam2D_Add(RDK.AddFrame(CAM_NAME + ' Frame'), CAM_PARAMS)
        cam_item.setName(CAM_NAME)
    cam_item.setParam('Open', 1)

    while cam_item.setParam('isOpen') == '1':
        img_socket = None
        bytes_img = RDK.Cam2D_Snapshot('', cam_item)
        if isinstance(bytes_img, bytes) and bytes_img != b'':
            nparr = np.frombuffer(bytes_img, np.uint8)
            img_socket = cv.imdecode(nparr, cv.IMREAD_COLOR)


        if img_socket is None:
            break
    





##########################################################



def load_box():
    global box_counter
    parent_path = os.path.dirname(__file__)+"\\" if 'nt' in os.name else "~//" 
    box_path = f"{parent_path}box.sld"
    box_item = RDK.AddFile(box_path)
    box = RDK.Item(box_item.Name())
    box_counter += 1
    box.setName("box_" + str(box_counter))  # box에 고유한 이름 부여
    return box

class modbus_inst():
    def __init__(self, host='127.0.0.1', port=502, unit_id=1):
        self.databank = DataBank()
        self.server = ModbusServer(host=host, port=port, no_block=True, data_bank=self.databank)

        self.server.start()
        self.heartbeat_flag = 0

        # 주소 0에서 9까지 초기값을 0으로 설정합니다.
        for address in range(15):
            self.databank.set_holding_registers(address, [0])

    def write_data(self, address, data):
        if type(data) == type([]):
            self.databank.set_holding_registers(address, data)
        else:
            self.databank.set_holding_registers(address, [data])

    def read_data(self, address, num = 1):
        data = self.databank.get_holding_registers(address, num)
        if num == 1:
            return [data[0]] if data else None
        else:
            return data if data else None

def define_model():
    all_items = RDK.ItemList()
    for item in all_items:
        print(item.Name())
    items = {}
    for item in all_items:
        items[item.Name()] = item
    return items


box_counter = 0
def load_box():
    global box_counter
    parent_path = os.path.dirname(__file__)+ ("\\" if 'nt' in os.name else "/" )
    box_path = f"{parent_path}box.sld"
    box_item = RDK.AddFile(box_path)
    box = RDK.Item(box_item.Name())
    box_counter += 1
    box.setName("box_" + str(box_counter))  # box에 고유한 이름 부여
    return box

def find_child_item(parent_item, child_name):
    child_items = parent_item.Childs()
    for item in child_items:
        if child_name in item.Name():
            return item
    return None

def delete_item(item_name):
    all_items = RDK.ItemList()
    for item in all_items:
        if item_name in item.Name():
            # 특정 item 이름이 item에 포함되어 있으면
            item.Delete()  # 해당 아이템을 삭제합니다.


items = define_model()
gantry = items["gantry"]
gripper = items["gripper"]
conveyor = items["conveyor"]
gripper_TCP = items["gripper_TCP"]
conveyor_TCP = items["conveyor_TCP"]
con_pitch = items["con_pitch"]
con_home = items["con_home"]

pallet = items["pallet"]

gantry_home = RDK.Item("gantry_home")
open_gripper = RDK.Item("open_gripper")
close_gripper = RDK.Item("close_gripper")
IN_pickup = RDK.Item("IN_pickup")
UP_pickup = RDK.Item("UP_pickup")

# 갠트리 홈밍
def home_motions(gantry, gripper, conveyor, gantry_home, open_gripper, con_pitch):
    gantry.MoveJ(gantry_home.Joints())
    gripper.MoveJ(open_gripper.Joints())
    conveyor.MoveJ(con_pitch)

# 각 축에 대해 사용자 정의 개의 포인트 생성
def make_points(x, y, z):
    base_point = [4200, 550, 1050]
    points = []
    x_pitch = 500 # 500
    y_pitch = 500 # 300
    z_pitch = -135

    for k in range(z):
        for j in range(y):
            for i in range(x):
                new_point = [base_point[0] + (i+1)*x_pitch,
                            base_point[1] + (j+1)*y_pitch,
                            base_point[2] + (k+1)*z_pitch]
                points.append(new_point)
    return points

# 티칭포인트를 RoboDK에 추가
def create_frames_and_targets(points, gantry, RDK, pallet, x, y, z):
    for idx, point in enumerate(points):
        point_name = f'Point_{(idx%x)+1:02}-{(idx//x%y)+1:02}-{(idx//(x*y)%z)+1:02}'
        frame_name = f'TeachingPoints_{(idx%x)+1:02}-{(idx//x%y)+1:02}-{(idx//(x*y)%z)+1:02}'

        gantry.MoveJ([point[0], point[1], 0], blocking=True)
        gantry.MoveJ(point, blocking=True)

        target_point = gantry.Pose()

        frame = RDK.AddFrame(frame_name)
        frame.setPose(target_point)
        frame.setParent(pallet)
        frame.setVisible(visible=False, visible_frame=False)
        target = RDK.AddTarget(point_name, frame)
        gantry.MoveJ([point[0], point[1], 0], blocking=True)

def move_to_target_forFULL(target_name, i, x, y, z):
    box = conveyor_material_input()
    target_name = f"Point_{(i%x)+1:02}-{(i//x%y)+1:02}-{(i//(x*y)%z)+1:02}"
    target = items[target_name]
    Frame = items[f'TeachingPoints_{(i%x)+1:02}-{(i//x%y)+1:02}-{(i//(x*y)%z)+1:02}']
    pretarget = target.Joints()
    pretarget[2] = 0
    gantry.MoveJ(pretarget, blocking=True)
    gantry.MoveJ(target.Joints(), blocking=True)
    gripper.MoveJ(open_gripper.Joints(), blocking=True)

    box.setParent(Frame)

    gantry.MoveJ(pretarget, blocking=True)

# ------------------------------

# 박스준비 onConveyor
def conveyor_material_input():
    conveyor.MoveJ(con_pitch)
    box = load_box()
    box.setParent(conveyor_TCP)
    conveyor.MoveJ(con_home)
    gantry.MoveJ(UP_pickup.Joints())
    gantry.MoveJ(IN_pickup.Joints())
    gripper.MoveJ(close_gripper.Joints())
    box.setParent(gripper_TCP)
    conveyor.MoveJ(con_pitch)
    gantry.MoveJ(UP_pickup.Joints())
    return box

def remove_box_from_conveyor(box):
    gantry.MoveJ(UP_pickup.Joints())
    gantry.MoveJ(IN_pickup.Joints())
    gripper.MoveJ(open_gripper.Joints())
    box.setParent(conveyor_TCP)
    conveyor.MoveJ(con_home)
    conveyor.MoveJ(con_pitch)
    gantry.MoveJ(UP_pickup.Joints())
    delete_item(box.Name())

# def move_to_out(gantry, gripper, x1, yy, zz):
def move_to_out(x, y, z):
    position_name = f"Point_{x:02}-{y:02}-{z:02}"
    frame_name = f"TeachingPoints_{x:02}-{y:02}-{z:02}"
    parent_item = items[frame_name]
    child_item = find_child_item(parent_item, "box_")
    target = items[position_name].Joints()
    pre_target = target.copy()
    pre_target[2] = 0

    gripper.MoveJ(open_gripper.Joints())
    gantry.MoveJ(pre_target, blocking=True)
    gantry.MoveJ(target, blocking=True)

    child_item.setParent(gripper_TCP)
    gripper.MoveJ(close_gripper.Joints())

    gantry.MoveJ(pre_target, blocking=True)
    gantry.MoveJ(UP_pickup.Joints())
    conveyor.MoveJ(con_home)
    gantry.MoveJ(IN_pickup.Joints())
    gripper.MoveJ(open_gripper.Joints())
    child_item.setParent(conveyor_TCP)

    gantry.MoveJ(UP_pickup.Joints())
    conveyor.MoveJ(con_pitch)
    child_item.Delete()

def move_to_in(x, y, z):
    box = conveyor_material_input()
    target_name = f"Point_{x:02}-{y:02}-{z:02}"
    target = items[target_name]
    Frame = items[f'TeachingPoints_{x:02}-{y:02}-{z:02}']
    pretarget = target.Joints()
    pretarget[2] = 0
    gantry.MoveJ(pretarget, blocking=True)
    gantry.MoveJ(target.Joints(), blocking=True)
    gripper.MoveJ(open_gripper.Joints(), blocking=True)

    box.setParent(Frame)

    gantry.MoveJ(pretarget, blocking=True)


def move_to_position(x1, y1, z1, x2, y2, z2):
    position_name = f"Point_{x1:02}-{y1:02}-{z1:02}"
    frame_name = f"TeachingPoints_{x1:02}-{y1:02}-{z1:02}"
    parent_item = items[frame_name]
    child_item = find_child_item(parent_item, "box_")
    target = items[position_name].Joints()
    pre_target = target.copy()
    pre_target[2] = 0

    gripper.MoveJ(open_gripper.Joints())
    gantry.MoveJ(pre_target, blocking=True)
    gantry.MoveJ(target, blocking=True)

    child_item.setParent(gripper_TCP)
    gripper.MoveJ(close_gripper.Joints())

    gantry.MoveJ(pre_target, blocking=True)


    target_name = f"Point_{x2:02}-{y2:02}-{z2:02}"
    target = items[target_name]
    Frame = items[f'TeachingPoints_{x2:02}-{y2:02}-{z2:02}']
    pretarget = target.Joints()
    pretarget[2] = 0
    gantry.MoveJ(pretarget, blocking=True)
    gantry.MoveJ(target.Joints(), blocking=True)
    gripper.MoveJ(open_gripper.Joints(), blocking=True)

    child_item.setParent(Frame)

    gantry.MoveJ(pretarget, blocking=True)

# ------------------------------

# x = 4; y = 4; z = 2
# points = make_points(x, y, z)
# create_frames_and_targets(points, gantry, RDK, pallet, x, y, z)

# create_frames_and_targets(make_points(20,6,5), gantry, RDK, pallet, 20, 6, 5)



home_motions(gantry, gripper, conveyor, gantry_home, open_gripper, con_pitch)

# items = define_model()
# for i in range(len(points)):
#     move_to_target_forFULL('dummy', i, x, y, z)

# items = define_model()

# move_to_in(1, 3, 2)


# move_to_out( 1, 1, 2)

# move_to_position(4,4,2,3,3,2)

# delete_item("box")
# items = define_model()
# add_model.save_model()
modbus_table = [0] * 20

if __name__ == '__main__':

    s = modbus_inst(
        port=502 if 'nt' in os.name else 2502


    )
    # s.write_data(address=11, data=0)
    # s.write_data(address=12, data=1)
    # s.write_data(address=13, data=0)
    s.write_data(address=11, data=[0,1,0])
    modbus_table = modbus_table[:11]+[0,1,0]+modbus_table[14:]
    logger.info(f" plc_ready : {modbus_table}")

    cam_streamer = Thread(target=camera_stream, daemon=True)
    cam_streamer.start()

    while True:
        s.databank.set_holding_registers(10, [s.heartbeat_flag])

        recv_data = s.read_data(address=0, num = 20)
        modbus_table = recv_data
        logger.info(f" plc_data_reading : {modbus_table}")

        # if not s.read_data(address=0):
        # if not recv_data[0]:

            

        if recv_data[0] == 1 and recv_data[13] == 0:
            # s.write_data(address=0,data=0)

            # 모드버스 11번 주소에 1을 작성하고 모드버스 12번 주소에 0을 작성
            # s.write_data(address=11, data=1)
            # s.write_data(address=12, data=0)
            s.write_data(address=11, data=[1,0,0])
            modbus_table = modbus_table[:11]+[1,0,0]+modbus_table[14:]
            logger.info(f" plc_mission_recived : {modbus_table[1:4]} -> {modbus_table[5:8]}")
            logger.info(f" plc_mission_running : {modbus_table}")


            data_x1 = recv_data[1]
            data_y1 = recv_data[2]
            data_z1 = recv_data[3]

            data_x2 = recv_data[5]
            data_y2 = recv_data[6]
            data_z2 = recv_data[7]

            if data_x1 == 0 and data_y1 == 0 and data_z1 == 0:
                move_to_in(data_x2, data_y2, data_z2)
            elif data_x2 == 0 and data_y2 == 0 and data_z2 == 0:
                move_to_out(data_x1, data_y1, data_z1)
            else:
                move_to_position(data_x1, data_y1, data_z1, data_x2, data_y2, data_z2)

            # s.write_data(address=11, data=0)
            # s.write_data(address=12, data=1)
            
            

            # 함수 실행이후 
            # 모드버스 11번 주소에 0을 작성하고 모드버스 12번, 13번 주소에 1을 작성
            # s.write_data(address=11, data=0)
            # s.write_data(address=12, data=1)
            # s.write_data(address=13, data=1)
            s.write_data(address=11, data=[0,1,1])
            modbus_table = modbus_table[:11]+[0,1,1]+modbus_table[14:]
            logger.info(f" plc_mission_fin : {modbus_table}")

        elif recv_data[0] == 0:
            # 함수 실행이후 초기화 이전 13번 주소에 0을 작성
            s.write_data(address=13, data=0)


        # DataBank 상태 출력
        print("Holding Registers from address 0 to 12:   ", s.databank.get_holding_registers(0, 13))

        sleep(0.2)
        

        print("=======================================================")

