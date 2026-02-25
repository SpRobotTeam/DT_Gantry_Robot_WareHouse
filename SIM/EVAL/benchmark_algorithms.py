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

from ERROR.error import NotEnoughSpaceError, ProductNotExistError  # noqa: E402
from main import main as WCSMain  # noqa: E402

# main.py가 등록한 INFO 핸들러를 조용히 만들어 벤치마크 출력 폭주를 막는다.
logger = logging.getLogger("main")
logger.setLevel(logging.WARNING)
for h in logger.handlers:
    h.setLevel(logging.WARNING)


def _line_count(file_path):
    with open(file_path, "r", newline="") as f:
        return sum(1 for _ in f)


def ensure_mission_list(seed, mission_count):
    mission_file = ROOT / "SIM" / "EVAL" / "mission_list" / f"mission_list_SEED-{seed:06d}.csv"
    required = max(mission_count, 1000)

    if mission_file.exists() and _line_count(mission_file) >= required:
        return mission_file

    gen_script = ROOT / "SIM" / "EVAL" / "mission_list_generator.py"
    print(f"[gen] SEED={seed:06d}, rows={required:,}")
    subprocess.check_call([sys.executable, str(gen_script), str(seed), str(required)])
    return mission_file


def load_missions(mission_file, mission_count):
    missions = []
    with open(mission_file, "r", newline="") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i >= mission_count:
                break
            missions.append(row)
    return missions


def build_la_freq_table(missions):
    counts = {}
    for row in missions:
        if len(row) >= 3 and row[1] == "OUT":
            pname = f"{int(row[2]):02d}"
            counts[pname] = counts.get(pname, 0) + 1
    if not counts:
        return {}
    max_count = max(counts.values())
    if max_count == 0:
        return {}
    return {k: v / max_count for k, v in counts.items()}


def run_simulation(seed, algo, missions):
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
        "seed": seed,
        "algo": algo,
        "missions": len(missions),
        "xy_distance": round(sum_distance[0], 3),
        "z_distance": round(sum_distance[1], 3),
        "total_distance": round(sum_distance[0] + sum_distance[1], 3),
        "unit_time": round(unit_time_past, 3),
        "height_std": round(std, 6),
        "in_count": counts["IN"],
        "out_count": counts["OUT"],
        "wait_count": counts["WAIT"],
        "skip_full": counts["skip_full"],
        "skip_empty": counts["skip_empty"],
        "elapsed_sec": round(elapsed, 3),
    }


def print_summary(results, algos):
    print("\n=== Benchmark Summary ===")
    by_seed = {}
    for row in results:
        by_seed.setdefault(row["seed"], {})[row["algo"]] = row

    for seed in sorted(by_seed):
        print(f"\n[SEED {seed:06d}]")
        ff_total = by_seed[seed].get("FF", {}).get("total_distance")
        for algo in algos:
            if algo not in by_seed[seed]:
                continue
            r = by_seed[seed][algo]
            msg = (
                f"{algo:>2} | total={r['total_distance']:>10,.1f} "
                f"(xy={r['xy_distance']:>10,.1f}, z={r['z_distance']:>9,.1f}) "
                f"| std={r['height_std']:.4f} | elapsed={r['elapsed_sec']:.2f}s"
            )
            if ff_total and algo != "FF":
                improve = (1.0 - (r["total_distance"] / ff_total)) * 100.0
                msg += f" | vs FF {improve:+.2f}%"
            print(msg)


def write_csv(results, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    if not results:
        return

    fieldnames = list(results[0].keys())
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def parse_args():
    parser = argparse.ArgumentParser(description="WCS 알고리즘 벤치마크")
    parser.add_argument("--seeds", type=int, nargs="+", default=[123456], help="평가 SEED 목록")
    parser.add_argument(
        "--algos",
        type=str,
        nargs="+",
        default=["FF", "RL", "LA", "RA"],
        help="평가 알고리즘 목록 (FF RL LA RA)",
    )
    parser.add_argument("--missions", type=int, default=20000, help="평가 미션 수")
    parser.add_argument(
        "--output",
        type=str,
        default="docs/viz/benchmark_results.csv",
        help="CSV 결과 파일 경로",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    algos = [a.upper() for a in args.algos]
    valid = {"FF", "RL", "LA", "RA"}
    invalid = [a for a in algos if a not in valid]
    if invalid:
        raise ValueError(f"지원하지 않는 알고리즘: {invalid}")

    results = []

    for seed in args.seeds:
        mission_file = ensure_mission_list(seed, args.missions)
        missions = load_missions(mission_file, args.missions)
        print(f"\n[seed={seed:06d}] missions={len(missions):,}")

        for algo in algos:
            print(f"  - run {algo}")
            row = run_simulation(seed=seed, algo=algo, missions=missions)
            results.append(row)

    output = ROOT / args.output
    write_csv(results, output)
    print_summary(results, algos)
    print(f"\nSaved: {output}")


if __name__ == "__main__":
    main()
