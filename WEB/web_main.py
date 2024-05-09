import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
# current_working_directory = os.getcwd()

import streamlit as st
import streamlit.components.v1 as components
import webbrowser as wb
# from WCS import SPWCS
import random as rand
import time
import datetime as dt
from MW import PLC_com
# from MW.DB_handler import


from main import main 

st.set_page_config(
    page_title='DT 기반 갠트리 자동 창고 제어 페이지',
    layout='wide',
    
                   )
st.title('DT 기반 갠트리 자동 창고 제어 페이지')


ip_addres = '192.168.0.40'

SPDTw = main()


default_setting = True

if default_setting:
    SPDTw.default_setting(container_name="default")



col1, col2, col3 = st.columns([.5,.05,.45])

with col3:
    os.path.dirname(__file__)+"\\"
    components.iframe(src=f"http://{ip_addres}:8091/", width=600, height=600, )

    if st.button("WMS", 'wms_bt'):
        wb.open_new_tab(f"http://{ip_addres}:8069/web#action=244&model=stock.picking.type&view_type=kanban&cids=3&menu_id=111")


with col1:
    
    tab_titles = ['입고', '출고', '정보 등록/수정', '재고 목록', '제어']
    inbound_tab, outbount_tab, info_edit_tab, invenrory_tab, control_tab = st.tabs(tab_titles)

    with inbound_tab: # 입고 탭
        st.write("상품 입고")
        
        selected_product = st.selectbox("입고 제품",list(SPDTw.wcs_DT.container_dict.keys()))
        reserved =  st.checkbox("입고 예약")
        if reserved:
            reserved_time = st.time_input("예약 시간", )
        else:
            reserved_time = None

        
        number = st.text_input("입고 수량", )
        if not number:
            number = '12'
        elif not number.isdecimal():
            st.write("입고 수량은 숫자로 적어주세요.")
        
        if st.button("입고", disabled=not number.isdecimal()):
            number = int(number)
            for i in range(number):
                SPDTw.wcs_DT.Inbound(
                    product_name=selected_product,
                    DOM=dt.datetime.now() if not reserved else reserved_time,
                    reserved_time = reserved_time
                    )
            
            

    with outbount_tab: # 출고 탭
        st.write("상품 출고")

        selct_all_items = False
        outbound_option = ["lot 직접 지정", "순차 출고(선입선출)", "무작위 출고"]
        outbound_order = st.radio("출고 방식", outbound_option)
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

        target_lot = number = None

        outbound_enable = True
        if outbound_order !=  outbound_option[0]:
            
            selct_all_items = st.checkbox("모든 상품 출고", value=selct_all_items)

            if selct_all_items:
                number = f'{len(SPDTw.wcs_DT.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict[SPDTw.Area_name].inventory)}'
            else:
                number = st.text_input("출고 수량", )
            if not number:
                number = '12'
            elif not number.isdecimal():
                st.write("출고 수량은 숫자로 적어주세요.")
                outbound_enable = False

        else:
            number = '1'
            # lot_input:str = st.text_input("lot 번호 입력")
            # if lot_input:
            #     for s in lot_input.split():
            #         for i in inventory:
            #             if (s == lot_input.split()[-1] 
            #                 and lot_input.isdecimal() 
            #                 and (f"{lot_input:04d}" in i[-4:])):
            #                 number = 1
            #                 lot = i
            #             else:
            #                 if s
            lot = st.selectbox("재고 리스트", SPDTw.wcs_DT.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict[SPDTw.Area_name].inventory)
            # st.write(lot)
            outbound_enable = True
        

        reserved =  st.checkbox("출고 예약")
        if reserved:
            reserved_time = st.time_input("예약 시간", )
        else:
            reserved_time = None

        if st.button("출고", disabled=not number.isdecimal()):
            number = int(number)
            target_lot = None
            
            for i in range(number):
                if outbound_order !=  outbound_option[0]:
                    if outbound_order !=  outbound_option[1]:
                        lot_num = 0
                    else:
                        lot_list = list(SPDTw.wcs_DT.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict[SPDTw.Area_name].inventory.keys())
                        lot_num = rand.choice(list(SPDTw.wcs_DT.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict[SPDTw.Area_name].inventory.keys()))
                    target_lot = SPDTw.wcs_DT.WH_dict[SPDTw.WH_name].Zone_dict[SPDTw.Zone_name].Area_dict[SPDTw.Area_name].inventory.pop(lot_num)
                
                SPDTw.wcs_DT.Outbound(
                    lot=target_lot , 
                    reserved_time = reserved_time
                    )    


    with info_edit_tab: # 정보 등록/수정 탭
        st.write("새로운 제품, 컨테이너, 공간 템플렛 등록 또는 수정")
        edit_dict = {
                    "상품 정보" : SPDTw.wcs_DT.product_templet_dict.keys(), 
                    "컨테이너 정보" : SPDTw.wcs_DT.container_dict.keys(), 
                    "저장 공간 정보"  : SPDTw.wcs_DT.WH_dict.keys()
                    }
        edit_section = st.radio("수정할 정보", list(edit_dict.keys()))
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)



    with invenrory_tab:  # 재고 목록 확인 탭
        st.write("현재 재고 목록")
    
    
    with control_tab:
        st.write("시스템 제어")
        if st.button("WCS 리셋"):
            SPDTw.reset(container_name="default")


    
    


