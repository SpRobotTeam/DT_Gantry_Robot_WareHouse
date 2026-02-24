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


---

## 📖 상세 사용법 가이드

### 시작하기
시스템을 사용하기 전에 다음 단계를 순서대로 따라하세요:

1. **환경 확인**
   ```bash
   python --version  # Python 3.6 이상 필요
   ```

2. **의존성 설치**
   ```bash
   pip install -r pip_requirements.txt
   ```

3. **RoboDK 설치** (시뮬레이션 사용 시)
   - [RoboDK 다운로드 페이지](https://robodk.com/ko/download)에서 설치

### 🎮 운영 모드별 사용법

시스템은 4가지 운영 모드를 지원합니다:

#### 1. 웹 인터페이스 모드 (권장)
```bash
streamlit run WEB/web_main.py
```

**웹 인터페이스 기능:**
- **입고 탭**: 제품 선택, 수량 입력, 예약 스케줄링
- **출고 탭**: FIFO/랜덤/직접 선택 출고, 벌크 출고
- **정보 등록/수정**: 제품, 컨테이너, 저장공간 관리
- **재고 목록**: 실시간 재고 모니터링
- **제어**: WCS 시스템 리셋 및 제어

**외부 시스템 연동:**
- WMS 시스템: `http://192.168.0.40:8069/`
- 모니터링 시스템: `http://192.168.0.40:8091/`

#### 2. 수동 모드 (대화형)
```bash
python main.py
# 모드 선택에서 Enter 키만 누르기
```

**수동 모드 명령어:**
- `n [상품명]`: 상품 템플릿 등록 (기본값: 'default')
- `i [수량]`: 입고 처리 (기본값: 8개)
- `o [수량]`: 출고 처리 (기본값: 전체)
- `p [lot번호]`: 특정 상품 출고
- `l`: 구역 물품 리스트 출력
- `c`: 시스템 종료

**사용 예시:**
```bash
>> n 제품A          # 제품A 템플릿 생성
>> i 10             # 10개 입고
>> l                # 재고 확인
>> o 5              # 5개 출고
>> c                # 종료
```

#### 3. 시뮬레이션/테스트 모드
```bash
python main.py
# 모드 선택: 'N' 입력 (시뮬레이션 없음) 또는 'S' 입력 (평가 모드)
# SEED 입력: 6자리 숫자 (예: 123456)
```

**평가 모드 기능:**
- 성능 벤치마킹
- 알고리즘 비교 (First-Fit vs Adaptive Optimization)
- 자동화된 미션 실행
- 종합 점수 산출

#### 4. 하드웨어 연동 모드
```bash
# 1단계: RoboDK 시뮬레이션 시작
python SIM/RoboDK/plc_motion006.py

# 2단계: WCS 시스템 시작 (새 터미널)
python main.py
```

### 📋 명령어 레퍼런스

#### 웹 인터페이스 단축키
| 기능 | 위치 | 설명 |
|------|------|------|
| 입고 처리 | 입고 탭 | 제품 선택 후 수량 입력 |
| FIFO 출고 | 출고 탭 → 순차 출고 | 가장 오래된 상품부터 출고 |
| 랜덤 출고 | 출고 탭 → 무작위 출고 | 임의 상품 출고 |
| 재고 확인 | 재고 목록 탭 | 실시간 재고 현황 |
| 시스템 리셋 | 제어 탭 | 전체 시스템 초기화 |

#### CLI 명령어 상세
| 명령어 | 매개변수 | 예시 | 설명 |
|--------|----------|------|------|
| `n` | [상품명] | `n 상품A` | 새 상품 템플릿 생성 |
| `i` | [수량] | `i 15` | 지정 수량 입고 |
| `o` | [수량] | `o 10` | 지정 수량 출고 |
| `p` | [lot번호] | `p 1234` | 특정 lot 출고 |
| `l` | 없음 | `l` | 재고 리스트 출력 |
| `c` | 없음 | `c` | 시스템 종료 |

### 📊 성능 모니터링

#### 시스템 상태 확인
```bash
# 로그 파일 확인
tail -f logs/main.log

# 재고 상태 확인 (웹 인터페이스)
# http://localhost:8501 → 재고 목록 탭

# PLC 통신 상태 확인
tail -f logs/plc_motion006.log
```

#### 성능 지표
- **시간 점수**: 로봇 이동 거리 기반 효율성
- **위치 점수**: 저장 공간 분산도 (표준편차)
- **통합 점수**: 시간 × 위치 점수 조합

### 🔧 문제해결 FAQ

#### Q1: 웹 인터페이스가 시작되지 않을 때
```bash
# 포트 사용 확인
netstat -an | grep 8501

# Streamlit 재설치
pip uninstall streamlit
pip install streamlit==1.28.2

# 방화벽 확인 (Linux)
sudo ufw allow 8501
```

#### Q2: RoboDK 연결 실패
```bash
# RoboDK 서비스 상태 확인
ps aux | grep RoboDK

# 포트 확인 (기본: 20500)
netstat -an | grep 20500

# 재시작
python SIM/RoboDK/plc_motion006.py
```

#### Q3: Modbus 통신 오류
```bash
# PLC 시뮬레이터 시작
python MW/modbus_sim.py

# 네트워크 연결 확인
ping 192.168.0.40
telnet 192.168.0.40 502
```

#### Q4: 의존성 설치 오류
```bash
# Qt5 웹소켓 설치 (Ubuntu/Debian)
sudo apt-get install libqt5websockets5-dev

# Python 버전 확인
python --version  # 3.6 이상 필요

# 권한 문제 해결
pip install --user -r pip_requirements.txt
```

#### Q5: 로그 파일이 생성되지 않을 때
```bash
# logs 디렉토리 생성
mkdir -p logs

# 권한 확인
chmod 755 logs/
touch logs/main.log
```

### 🌐 네트워크 설정

#### 기본 설정
- **WCS 포트**: 기본 Python 실행
- **웹 인터페이스**: 8501 포트
- **Modbus TCP**: 502 포트
- **RoboDK**: 20500 포트

#### 외부 시스템 연동
```bash
# 네트워크 설정 확인
cat network.ps1

# IP 주소 설정 (필요시 수정)
# WMS: 192.168.0.40:8069
# 모니터링: 192.168.0.40:8091
```

### 📈 고급 사용법

#### 알고리즘 커스터마이징
시스템은 두 가지 최적화 알고리즘을 지원합니다:
- **First-Fit (FF)**: 빠른 배치, 단순한 로직
- **Adaptive Optimization (AO)**: 공간 효율성 최적화

`WCS/Info_mng.py`에서 알고리즘 선택 가능.

#### 배치 작업 스크립팅
```python
# 예시: 대량 입고 스크립트
from main import main

wcs = main()
wcs.default_setting(container_name='대량처리')

# 100개 제품 자동 입고
for i in range(100):
    wcs.Inbound(product_name='제품A')
```

## QnA
### 문의처
maroon@spsystems.co.kr