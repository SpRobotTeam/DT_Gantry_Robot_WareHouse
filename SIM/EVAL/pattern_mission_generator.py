"""
패턴 변화 미션 리스트 생성기

RA 알고리즘의 적응력을 검증하기 위한 시간 변화 출고 패턴 지원.

지원 패턴:
  uniform  - 균등 분포 (기준선)
  shift    - 전반 01 집중 → 후반 04 집중 (2단계 전환)
  shift3   - 3단계 전환: 01 → 02+03 → 04
  cyclic   - cycle_len 미션마다 인기 품목 01→02→03→04 순환
  burst    - 기본 균등, 30~50% 구간에 01 집중 폭발 후 복귀
"""

import bisect
import datetime as dt
import random
from typing import List

ITEM_TYPES = ['01', '02', '03', '04']
BASE_IN_FREQ = [1.0, 1.0, 1.0, 1.0]
ACTION_WEIGHTS = [0.5, 0.3, 0.2]   # IN, OUT, WAIT


def _out_weights(pattern: str, step: int, total: int, cycle_len: int) -> List[float]:
    """현재 스텝의 OUT 품목 가중치 반환"""
    if pattern == 'shift':
        # 전반 50%: 01 집중 / 후반 50%: 04 집중
        return [5.0, 1.0, 1.0, 1.0] if step < total * 0.5 else [1.0, 1.0, 1.0, 5.0]

    elif pattern == 'shift3':
        # 3단계: 01 집중 → 02+03 혼합 → 04 집중
        if step < total / 3:
            return [6.0, 1.0, 1.0, 1.0]
        elif step < total * 2 / 3:
            return [1.0, 3.0, 3.0, 1.0]
        else:
            return [1.0, 1.0, 1.0, 6.0]

    elif pattern == 'cyclic':
        # cycle_len 미션마다 인기 품목이 01→02→03→04 순환
        phase = (step // cycle_len) % len(ITEM_TYPES)
        w = [1.0] * len(ITEM_TYPES)
        w[phase] = 6.0
        return w

    elif pattern == 'burst':
        # 기본 균등, 30~50% 구간에만 01 집중 burst
        if total * 0.30 <= step < total * 0.50:
            return [8.0, 1.0, 1.0, 1.0]
        else:
            return [1.0, 1.0, 1.0, 1.0]

    else:  # uniform
        return [1.0, 1.0, 1.0, 1.0]


def generate(
    seed: int,
    mission_count: int,
    pattern: str = 'shift',
    cycle_len: int = 2000,
) -> List[list]:
    """
    패턴 변화 미션 리스트를 메모리상으로 생성하여 반환.

    반환 형식: [[iter, action, product_id, dom?], ...]
    CSV 미션 파일과 동일한 행 구조.

    Parameters
    ----------
    seed          : 난수 SEED
    mission_count : 생성할 미션 수
    pattern       : 'uniform' | 'shift' | 'shift3' | 'cyclic' | 'burst'
    cycle_len     : cyclic 패턴의 주기 (미션 수 단위)
    """
    rng = random.Random(seed)
    items_by_product: dict = {pid: [] for pid in ITEM_TYPES}
    total_items = 0
    item_id = 0
    last_action = ''
    rows: List[list] = []

    base_date = dt.datetime(2020, 1, 1)
    date_range = (dt.datetime(2025, 12, 12) - base_date).days

    iteration = 1
    while len(rows) < mission_count:
        step = len(rows)
        out_w = _out_weights(pattern, step, mission_count, cycle_len)

        # 액션 선택
        if item_id == 0:
            action = 'IN'
        else:
            action = rng.choices(['IN', 'OUT', 'WAIT'], weights=ACTION_WEIGHTS)[0]
            if action == 'WAIT' and last_action == 'WAIT':
                continue
            if action == 'OUT' and total_items == 0:
                continue

        if action == 'IN':
            pid = rng.choices(ITEM_TYPES, weights=BASE_IN_FREQ)[0]
            dom = base_date + dt.timedelta(days=rng.randint(0, date_range))
            dom_str = f"{dom.year:04d}{dom.month:02d}{dom.day:02d}"
            item_id += 1
            bisect.insort(items_by_product[pid], (dom, item_id))
            total_items += 1
            rows.append([iteration, 'IN', pid, dom_str])
            last_action = 'IN'

        elif action == 'OUT':
            available = [pid for pid in ITEM_TYPES if items_by_product[pid]]
            if not available:
                continue
            avail_weights = [out_w[ITEM_TYPES.index(pid)] for pid in available]
            pid = rng.choices(available, weights=avail_weights)[0]
            items_by_product[pid].pop(0)
            total_items -= 1
            rows.append([iteration, 'OUT', pid])
            last_action = 'OUT'

        else:  # WAIT
            wait_time = rng.randint(61, 1800)
            rows.append([iteration, 'WAIT', str(wait_time)])
            last_action = 'WAIT'

        iteration += 1

    return rows[:mission_count]


def phase_out_stats(missions: List[list], n_phases: int = 4) -> dict:
    """
    미션 리스트를 n_phases 구간으로 나눠 각 구간의 OUT 품목 비율 반환.
    패턴이 실제로 의도대로 생성됐는지 검증용.
    """
    total = len(missions)
    phase_size = max(1, total // n_phases)
    stats = {}
    for p in range(n_phases):
        start = p * phase_size
        end = start + phase_size if p < n_phases - 1 else total
        counts: dict = {}
        for row in missions[start:end]:
            if row[1] == 'OUT':
                pid = str(row[2])
                counts[pid] = counts.get(pid, 0) + 1
        total_out = sum(counts.values()) or 1
        stats[f"phase{p+1}"] = {
            pid: round(cnt / total_out, 3)
            for pid, cnt in sorted(counts.items())
        }
    return stats
