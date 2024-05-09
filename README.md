# 제조 혁신을 위한 디지털 트원 적용


## 시스템 개요
디지털 트윈 시스템 개발
 - 창고형 갠트리 운영을 위한 디지털 트윈 시스템 구축


### 개념 정리 - 노션
[기본 페이지](https://cloudy-rule-316.notion.site/68288352350048ff82300f51217bb229?pvs=4)

### 개념 정리 - PPT
[개념](https://tuackr-my.sharepoint.com/:p:/g/personal/lmrlar98_tuackr_onmicrosoft_com/Ed7idKPbG_dJqUAPZ9F4i9wBHs6nexKCHy1koZ46b27GlA?e=WWGoAR)

[구성도](https://tuackr-my.sharepoint.com/:p:/g/personal/lmrlar98_tuackr_onmicrosoft_com/EbSxN29LyK5GroHN0bicSdkBxmI0hg_D7z7FpUDP1HTLPw?e=dMSdFW)


## 구성 요소

<!-- #### 박스 규격 통일 
300\*200\*200 mm (박스 간 간격 전후좌우 200mm)

#### 작업 구역 크기 
7000\*12000\*1600 mm -->

## 구현 단계
### WCS 구현
- [x] 기본 WCS 구현
    - [x] 입고, 출고 기록 및 상품 추적
    - [x] 자동 정렬
    - [ ] 최적화 알고리즘
    - [ ] 일정(스케쥴) 작성/수행
- [ ] MICUBE WCS 적용
    - [ ] 협의
        
        ...

### WMS 연동
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
- [ ] 시뮬레이션 최적화 알고리즘 구성

### 프론트 엔드
- [ ] 네트워크 설정
- [x] 왭 기반 제어 구현
    - [ ] 카메라 수정
- [ ] RoboDK 연동 UI
