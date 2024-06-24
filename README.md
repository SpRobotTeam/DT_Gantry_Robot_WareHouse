# 갠트리 로봇 창고 운영 시스템 - 제조 혁신을 위한 디지털 트원 적용


## 시스템 개요
디지털 트윈 시스템 개발
 - 창고형 갠트리 운영을 위한 디지털 트윈 시스템 구축

### 개념 정리 - 노션
[공유 페이지](https://expensive-chatter-5f2.notion.site/e5fbadc76a014c44bd19caba0a98b826?pvs=4 "프로젝트 노션 페이지")
<!-- 
[팀 노션 페이지](https://www.notion.so/DTw-395d57d4720445a4bf8d06fbc176af5e?pvs=4) -->


### 구성
시스템 플로우차트
![플로우 차트](https://github.com/SpRobotTeam/DT_Gantry_Robot_WareHouse/blob/basic_only/doc/%EA%B0%A0%ED%8A%B8%EB%A6%AC%20%EA%B8%B0%EB%B0%98%20DTw%20%EC%8B%9C%EC%8A%A4%ED%85%9C%20%EC%9E%91%EC%97%85%20%ED%9D%90%EB%A6%84%EB%8F%84.drawio.png)

<details>
  <summary><b>디렉토리 구조</b></summary>

```html
📦Gantry_robot_warehouse    
┣ 📂main.py                     # 전채 시스템 실행
┣ 📂WCS                         # 공간 구성, 편집 및 제어
┃   ┣ 📜SPWCS.py                # WCS 시스템
┃   ┣ 📜Info_mng.py             # 상품, 품목 등 정보 제어
┃   ┣ 📜WH_mng.py               # 창고 공간 제어
┃   ┣ 📜Zone_mng.py             # 중규모 공간 제어
┃   ┗ 📜Area_mng.py             # 소규모 공간 제어
┣ 📂MW
┃   ┣ 📜Company_mng.py          # 회사, 거래처 등 정보 구성, 편집
┃   ┣ 📜modbus_sim.py           # 모드버스 통신 (테스트용)
┃   ┣ 📜PLC_com.py              # 모드버스 통신
┃   ┗ 📜Product_mng.py          # 제품 품목 구성, 편집    
┣ 📂API                         
┃   ┣ 📜DB_mng.py               # DB 제어(적용 안됨)
┃   ┗ 📜odoo_api_wrapper.py     # WMS 연동 (적용 안됨)
┣ 📂SIM                         
┃   ┣ 📂EVAL                    # 알고리즘 평가
┃   ┃   ┣ 📜eval_list           # 평가 데이터
┃   ┃   ┗ 📜mission_list        # 미션 리스트
┃   ┣ 📂RoboDK                  # 시뮬레이션
┃   ┃   ┣ 📜plc_motion006.py    # 시뮬레이션 실행
┃   ┃   ┣ 📜wcs_plc_{DATE}.rdk  # 시뮬레이션 환경 파일
┃   ┃   ┗ 📜e.t.c ...           # 기타
┣ 📂ERROR                       # 에러 처리
┣ 📂logs                        # 로그
┣ 📂WEB                         # 웹 기반 구동
┗ 📜pip_requirements.txt        # 의존성 페키지 목록
```
</details>

## 시뮬레이션 설정/구성 요소

### 창고 크기
- 20x20x5로 변경 완료
    - 최대 수용 가능 크기 : 396개 (=20x20x5-(5-1))

<!-- #### -->
<!-- #### 박스 규격 통일 
300\*200\*200 mm (박스 간 간격 전후좌우 200mm)
#### 작업 구역 크기 
7000\*12000\*1600 mm -->
### 제품 품목
- '01' ~ '04' : 현재 품명 및 lot 번호 외 차이점 없음

## 설치 및 실행 (WMS 연동 없음)
1. OS 버전에 맞는 RoboDK 설치 -> [다운로드 페이지 (개인정보 입력 필요)](https://robodk.com/ko/download)
    - 설치위치와 기능은 기본 설정을 그대로 사용함 
2. git 레포지토리 복사
3. repository 디렉토리로 이동
    ``` 
    cd ./Gantry_robot_warehouse
    ```
4. 의존 패키지 설치 (Python 버전 3.6 이상 필요)
    - repository 디렉토리에서 아래 명령 실행
        ```
        pip install -r pip_requirements.txt
        ```
    - (오류 발생 시) QT5 웹 소켓 
        ```
        apt-get install libqt5websockets5-dev
        ```
5. RoboDK 시뮬레이션 실행
    ```
    python SIM\RoboDK\plc_motion006.py
    ```
6. WCS 실행 (다른 터미널에서)
    ```
    python main.py
    ```


## 구현 단계
### WCS 구현 
- [x] 기본 WCS 구현
    - [x] 입고, 출고 기록 및 상품 추적
    - [x] 자동 정렬
    - [ ] 최적화 알고리즘
    - [ ] 일정(스케쥴) 작성/수행
<!-- 
- [ ] MICUBE WCS 적용
- [ ] 협의 -->

### WMS 연동 (적용 안됨)
- [x] 오픈 소스 WMS 선정
- [x] 오픈 소스 WMS 설치
- [ ] 오픈 소스 WMS 연동
    - [ ] DB 연동
        - [x] DB API Wraper 구축
        - [x] 시스템 데이터 구조 통일
        - [ ] 시스템 데이터 상호 작용 구성
        - [ ] 시스템 데이터 구조 연동

### 시뮬레이션 
- [x] RoboDK 기반 시뮬레이션 구성
- [ ] 시뮬레이션/하드웨어 - WCS 연동 M/W 구성
- [ ] 시뮬레이션 최적화 알고리즘 협력 개발 (부산대)
- [ ] 시뮬레이션 최적화 알고리즘 보완 및 내재화

### 시스템 통합 및 프론트 엔드
- [ ] 외부 네트워크 설정 (포트 포워딩 등)
- [x] 왭 기반 제어 구현
    - [ ] 카메라 수정
- [ ] RoboDK 연동 UI 생성
- [ ] 시스템 통합
- [ ] 패키지로 작성 (제품화)


## QnA
### 문의처
maroon@spsystems.co.kr