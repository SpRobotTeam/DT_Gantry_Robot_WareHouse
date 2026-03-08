"""
WCS 알고리즘 벤치마크 스크립트

사용 예시:
  # 기본 (uniform 패턴, SEED 123456, 20000 미션)
  python SIM/EVAL/benchmark_algorithms.py

  # 패턴 변화 시나리오 비교
  python SIM/EVAL/benchmark_algorithms.py --pattern shift
  python SIM/EVAL/benchmark_algorithms.py --pattern cyclic --cycle-len 1000
  python SIM/EVAL/benchmark_algorithms.py --pattern burst

  # 여러 패턴 한 번에 비교
  python SIM/EVAL/benchmark_algorithms.py --pattern uniform shift cyclic burst

  # 전체 옵션
  python SIM/EVAL/benchmark_algorithms.py \\
      --seeds 123456 654321 \\
      --algos FF RL LA RA \\
      --missions 20000 \\
      --pattern uniform shift cyclic burst \\
      --cycle-len 2000 \\
      --output docs/viz/benchmark_results.csv
"""

import argparse
import csv
import os
import statistics
import subprocess
import sys
import time
import logging
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ERROR.error import NotEnoughSpaceError, ProductNotExistError          # noqa: E402
from main import main as WCSMain                                           # noqa: E402
from SIM.EVAL.pattern_mission_generator import generate as gen_pattern     # noqa: E402
from SIM.EVAL.pattern_mission_generator import phase_out_stats             # noqa: E402

# main.py가 등록한 INFO 핸들러를 조용히 만들어 벤치마크 출력 폭주를 막는다.
logger = logging.getLogger("main")
logger.setLevel(logging.WARNING)
for h in logger.handlers:
    h.setLevel(logging.WARNING)

VALID_PATTERNS = ("uniform", "shift", "shift3", "cyclic", "burst")
VALID_ALGOS    = {"FF", "RL", "LA", "RA"}


# ──────────────────────────────────────────────
# 미션 로딩
# ──────────────────────────────────────────────

def _line_count(file_path):
    with open(file_path, "r", newline="") as f:
        return sum(1 for _ in f)


def ensure_mission_list(seed: int, mission_count: int) -> Path:
    """uniform 패턴용: 파일 기반 미션 리스트 보장"""
    mission_file = ROOT / "SIM" / "EVAL" / "mission_list" / f"mission_list_SEED-{seed:06d}.csv"
    required = max(mission_count, 1000)
    if mission_file.exists() and _line_count(mission_file) >= required:
        return mission_file
    gen_script = ROOT / "SIM" / "EVAL" / "mission_list_generator.py"
    print(f"[gen] SEED={seed:06d}, rows={required:,}")
    subprocess.check_call([sys.executable, str(gen_script), str(seed), str(required)])
    return mission_file


def load_missions(mission_file: Path, mission_count: int) -> list:
    missions = []
    with open(mission_file, "r", newline="") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i >= mission_count:
                break
            missions.append(row)
    return missions


def get_missions(seed: int, mission_count: int, pattern: str, cycle_len: int) -> list:
    """패턴에 따라 미션 리스트 반환"""
    if pattern == "uniform":
        mfile = ensure_mission_list(seed, mission_count)
        return load_missions(mfile, mission_count)
    else:
        return gen_pattern(seed=seed, mission_count=mission_count,
                           pattern=pattern, cycle_len=cycle_len)


# ──────────────────────────────────────────────
# LA 빈도 테이블
# ──────────────────────────────────────────────

def build_la_freq_table(missions: list) -> dict:
    counts: dict = {}
    for row in missions:
        if len(row) >= 3 and row[1] == "OUT":
            pname = f"{int(row[2]):02d}"
            counts[pname] = counts.get(pname, 0) + 1
    if not counts:
        return {}
    max_count = max(counts.values())
    return {k: v / max_count for k, v in counts.items()} if max_count else {}


# ──────────────────────────────────────────────
# 시뮬레이션 실행
# ──────────────────────────────────────────────

def run_simulation(seed: int, algo: str, missions: list, pattern: str) -> dict:
    wcs = WCSMain(op_mode="n")
    wcs.mode = algo
    wcs.default_setting(container_name="default")

    if algo == "LA":
        wcs._freq_table = build_la_freq_table(missions)

    sum_distance = [0.0, 0.0]
    unit_time_past = 0.0
    speed = [1.0, 1.0]
    counts = {"IN": 0, "OUT": 0, "WAIT": 0, "skip_full": 0, "skip_empty": 0}
    start = time.time()

    for row in missions:
        action = row[1]

        if action == "IN":
            product_name = f"{int(row[2]):02d}"
            dom = row[3]
            try:
                moved, _lot = wcs.Inbound(product_name=product_name, DOM=dom, testing_mode=True)
                counts["IN"] += 1
            except NotEnoughSpaceError:
                counts["skip_full"] += 1
                continue
        elif action == "OUT":
            product_name = f"{int(row[2]):02d}"
            try:
                moved, _lot = wcs.Outbound(product_name=product_name, testing_mode=1)
                counts["OUT"] += 1
            except ProductNotExistError:
                counts["skip_empty"] += 1
                continue
        else:
            counts["WAIT"] += 1
            continue

        sum_distance[0] += moved[0]
        sum_distance[1] += moved[1]
        unit_time_past += (moved[0] * speed[0]) + (moved[1] * speed[1])

    elapsed = time.time() - start

    area = wcs.WH_dict[wcs.WH_name].Zone_dict[wcs.Zone_name].Area_dict["Area_01"]
    heights = [len(area.grid[x][y]) for x in range(area.COL) for y in range(area.ROW)]
    std = statistics.pstdev(heights) if heights else 0.0

    return {
        "pattern":       pattern,
        "seed":          seed,
        "algo":          algo,
        "missions":      len(missions),
        "xy_distance":   round(sum_distance[0], 3),
        "z_distance":    round(sum_distance[1], 3),
        "total_distance": round(sum_distance[0] + sum_distance[1], 3),
        "unit_time":     round(unit_time_past, 3),
        "height_std":    round(std, 6),
        "in_count":      counts["IN"],
        "out_count":     counts["OUT"],
        "wait_count":    counts["WAIT"],
        "skip_full":     counts["skip_full"],
        "skip_empty":    counts["skip_empty"],
        "elapsed_sec":   round(elapsed, 3),
    }


# ──────────────────────────────────────────────
# 결과 출력
# ──────────────────────────────────────────────

def print_summary(results: list, algos: list):
    print("\n" + "=" * 72)
    print("  Benchmark Summary")
    print("=" * 72)

    # (pattern, seed) → algo → result
    grouped: dict = {}
    for r in results:
        key = (r["pattern"], r["seed"])
        grouped.setdefault(key, {})[r["algo"]] = r

    for (pattern, seed) in sorted(grouped):
        algo_results = grouped[(pattern, seed)]
        ff_total = algo_results.get("FF", {}).get("total_distance")

        print(f"\n  [{pattern.upper():8s}] SEED={seed:06d}")
        print(f"  {'─' * 68}")

        for algo in algos:
            if algo not in algo_results:
                continue
            r = algo_results[algo]
            line = (
                f"  {algo:>2} | total={r['total_distance']:>12,.1f} "
                f"(xy={r['xy_distance']:>11,.1f}, z={r['z_distance']:>9,.1f}) "
                f"| std={r['height_std']:.4f} | {r['elapsed_sec']:.1f}s"
            )
            if ff_total and algo != "FF":
                improve = (1.0 - r["total_distance"] / ff_total) * 100.0
                line += f"  [{improve:+.2f}% vs FF]"
            print(line)

    # 패턴별 RA vs RL/LA 비교 요약 (패턴이 2개 이상인 경우)
    patterns_seen = sorted({r["pattern"] for r in results})
    if len(patterns_seen) >= 2:
        print(f"\n  {'─' * 68}")
        print("  패턴별 RA 상대 성능 (RA total_distance / RL total_distance)")
        print(f"  {'─' * 68}")
        seeds_seen = sorted({r["seed"] for r in results})

        header = f"  {'pattern':>10}"
        for seed in seeds_seen:
            header += f"  SEED={seed:06d}"
        print(header)

        for pattern in patterns_seen:
            line = f"  {pattern:>10}"
            for seed in seeds_seen:
                key = (pattern, seed)
                ar = grouped.get(key, {})
                ra_d  = ar.get("RA",  {}).get("total_distance")
                rl_d  = ar.get("RL",  {}).get("total_distance")
                if ra_d and rl_d and rl_d > 0:
                    ratio = ra_d / rl_d
                    mark = " ✓" if ratio <= 1.02 else "  "
                    line += f"  RA/RL={ratio:.3f}{mark}"
                else:
                    line += f"  {'N/A':>12}"
            print(line)
        print()


# ──────────────────────────────────────────────
# CSV 저장
# ──────────────────────────────────────────────

def write_csv(results: list, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    if not results:
        return
    fieldnames = list(results[0].keys())
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="WCS 알고리즘 벤치마크 (패턴 변화 시나리오 포함)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
패턴 설명:
  uniform  균등 분포 (기존 기준선)
  shift    전반 50%: 01 집중 → 후반 50%: 04 집중
  shift3   3단계 전환: 01 → 02+03 → 04
  cyclic   --cycle-len 미션마다 01→02→03→04 순환
  burst    30~50% 구간에 01 집중 burst 후 복귀

예시:
  python benchmark_algorithms.py --pattern shift cyclic --missions 20000
  python benchmark_algorithms.py --pattern cyclic --cycle-len 1000
        """
    )
    parser.add_argument("--seeds",    type=int, nargs="+", default=[123456])
    parser.add_argument("--algos",    type=str, nargs="+", default=["FF", "RL", "LA", "RA"])
    parser.add_argument("--missions", type=int, default=20000)
    parser.add_argument(
        "--pattern", type=str, nargs="+", default=["uniform"],
        choices=list(VALID_PATTERNS),
        metavar="PATTERN",
        help=f"패턴 목록: {', '.join(VALID_PATTERNS)}"
    )
    parser.add_argument("--cycle-len", type=int, default=2000,
                        help="cyclic 패턴 주기 (기본 2000)")
    parser.add_argument("--output", type=str,
                        default="docs/viz/benchmark_results.csv")
    parser.add_argument("--show-phase-stats", action="store_true",
                        help="패턴 구간별 OUT 품목 분포 출력 (검증용)")
    return parser.parse_args()


def main():
    args = parse_args()

    algos = [a.upper() for a in args.algos]
    invalid_algos = [a for a in algos if a not in VALID_ALGOS]
    if invalid_algos:
        raise ValueError(f"지원하지 않는 알고리즘: {invalid_algos}")

    patterns = args.pattern

    results = []

    for pattern in patterns:
        for seed in args.seeds:
            missions = get_missions(seed, args.missions, pattern, args.cycle_len)
            print(f"\n[pattern={pattern}, seed={seed:06d}] missions={len(missions):,}")

            # 패턴 검증 출력 (--show-phase-stats 옵션)
            if args.show_phase_stats:
                stats = phase_out_stats(missions, n_phases=4)
                for phase, dist in stats.items():
                    print(f"  {phase}: {dist}")

            for algo in algos:
                print(f"  - run {algo}", end="", flush=True)
                row = run_simulation(seed=seed, algo=algo,
                                     missions=missions, pattern=pattern)
                results.append(row)
                print(f"  →  total={row['total_distance']:>12,.1f}  ({row['elapsed_sec']:.1f}s)")

    output = ROOT / args.output
    write_csv(results, output)
    print_summary(results, algos)
    print(f"\nSaved: {output}")


if __name__ == "__main__":
    main()
