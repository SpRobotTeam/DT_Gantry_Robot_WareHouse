"""
RA 알고리즘 단독 시각화 HTML 생성 스크립트

Usage:
  python SIM/EVAL/gen_viz_ra.py               # SEED=123456, 100k 미션
  python SIM/EVAL/gen_viz_ra.py 123456 100000
"""

import csv
import json
import logging
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 로그 출력 억제 (모든 핸들러 WARNING 이상만)
logging.getLogger("main").setLevel(logging.WARNING)
for _name in ("Zone_mng", "Area_mng", "WH_mng", "SPWCS", "Info_mng"):
    logging.getLogger(_name).setLevel(logging.WARNING)

from ERROR.error import NotEnoughSpaceError, ProductNotExistError  # noqa
from main import main as WCSMain                                    # noqa
from SIM.EVAL.visualizer import VizCollector                        # noqa

SEED    = int(sys.argv[1]) if len(sys.argv) > 1 else 123456
MISSIONS = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
OUT_DIR  = ROOT / "docs" / "viz"


def load_missions(seed: int, count: int) -> list:
    mfile = ROOT / "SIM" / "EVAL" / "mission_list" / f"mission_list_SEED-{seed:06d}.csv"
    if not mfile.exists():
        import subprocess
        gen = ROOT / "SIM" / "EVAL" / "mission_list_generator.py"
        print(f"[gen] SEED={seed:06d}, rows={count}")
        subprocess.check_call([sys.executable, str(gen), str(seed), str(count)])
    rows = []
    with open(mfile, newline="") as f:
        for i, row in enumerate(csv.reader(f)):
            if i >= count:
                break
            rows.append(row)
    return rows


def _build_light_html(data_json: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>창고 배치 시각화</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'IBM Plex Sans', sans-serif; background: #f4f3f0; color: #2c2c2c; padding: 0; -webkit-font-smoothing: antialiased; }}
body::before {{ content:''; position:fixed; inset:0; background-image: linear-gradient(rgba(14,116,144,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(14,116,144,0.03) 1px, transparent 1px); background-size: 40px 40px; pointer-events:none; z-index:0; }}

.page-header {{ background: #1b2a3d; padding: 28px 20px 22px; text-align: center; position: relative; overflow: hidden; }}
.page-header::before {{ content:''; position:absolute; inset:0; background: linear-gradient(135deg, rgba(147,51,234,0.15) 0%, transparent 50%); }}
.page-header::after {{ content:''; position:absolute; bottom:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,rgba(147,51,234,0.4),transparent); }}
.page-header h1, .page-header .info-bar {{ position: relative; z-index: 1; }}
.back-link {{ position: absolute; left: 20px; top: 50%; transform: translateY(-50%); z-index: 2; color: rgba(255,255,255,0.5); text-decoration: none; font-size: 0.85em; font-family: 'IBM Plex Sans', sans-serif; transition: color 0.15s; }}
.back-link:hover {{ color: #d8b4fe; }}

h1 {{ text-align: center; margin-bottom: 10px; font-family: 'Outfit', sans-serif; font-size: 1.5em; font-weight: 700; color: #ffffff; letter-spacing: -0.02em; }}
.info-bar {{ display: flex; justify-content: center; gap: 20px; margin-bottom: 0; font-size: 0.85em; color: rgba(255,255,255,0.5); }}
.info-bar span {{ background: rgba(255,255,255,0.08); padding: 5px 15px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); }}
.info-bar .val {{ color: #d8b4fe; font-weight: 600; }}

.content-wrap {{ position: relative; z-index: 1; max-width: 1400px; margin: 0 auto; padding: 20px 20px 40px; }}

.main-layout {{ display: flex; gap: 20px; max-width: 1400px; margin: 0 auto; }}
.grid-panel {{ flex: 0 0 auto; }}
.chart-panel {{ flex: 1; min-width: 300px; }}
.grid-container {{ position: relative; }}
canvas#gridCanvas {{ border: 1px solid #e2e0db; border-radius: 8px; }}
.grid-legend {{ display: flex; align-items: center; gap: 10px; margin-top: 10px; font-size: 0.75em; color: #6b7280; }}
.legend-bar {{ display: flex; height: 16px; border-radius: 4px; overflow: hidden; flex: 1; border: 1px solid #e2e0db; }}
.legend-bar div {{ flex: 1; }}
.controls {{ text-align: center; margin: 16px 0; }}
.slider-wrap {{ display: flex; align-items: center; gap: 10px; max-width: 700px; margin: 0 auto; }}
.slider-wrap input[type=range] {{ flex: 1; accent-color: #9333ea; }}
.slider-wrap label {{ font-size: 0.85em; min-width: 150px; color: #6b7280; font-family: 'IBM Plex Mono', monospace; font-weight: 500; }}
.btn-group {{ margin-top: 10px; }}
.btn-group button {{ background: #ffffff; color: #9333ea; border: 1px solid #e2e0db; padding: 6px 18px;
    border-radius: 6px; cursor: pointer; margin: 0 4px; font-size: 0.85em; font-family: 'IBM Plex Sans', sans-serif; font-weight: 500; transition: all 0.15s; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}
.btn-group button:hover {{ background: #faf5ff; border-color: #9333ea; }}
.btn-group button.active {{ background: #9333ea; color: #ffffff; border-color: #9333ea; }}
.stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }}
.stat-card {{ background: #ffffff; border: 1px solid #e2e0db; border-radius: 10px; padding: 14px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }}
.stat-card .label {{ font-size: 0.75em; color: #9ca3af; }}
.stat-card .value {{ font-family: 'IBM Plex Mono', monospace; font-size: 1.3em; font-weight: 600; color: #9333ea; margin-top: 4px; }}
.chart-box {{ background: #ffffff; border: 1px solid #e2e0db; border-radius: 12px; padding: 18px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }}
.chart-box h3 {{ font-family: 'Outfit', sans-serif; font-size: 0.9em; color: #6b7280; margin-bottom: 12px; font-weight: 600; }}
canvas.chart {{ width: 100% !important; height: 180px !important; }}
.product-legend {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; font-size: 0.75em; color: #6b7280; }}
.product-legend .item {{ display: flex; align-items: center; gap: 4px; }}
.product-legend .swatch {{ width: 14px; height: 14px; border-radius: 4px; border: 1px solid #d1d5db; }}
.out-label {{ position: absolute; top: -22px; left: 0; font-size: 0.7em; color: #dc2626; font-weight: 500; }}
</style>
</head>
<body>
<div class="page-header">
<a href="index.html" class="back-link">&larr; 목록</a>
<h1>창고 격자 배치 시각화</h1>
<div class="info-bar">
    <span>SEED: <span class="val" id="infoSeed"></span></span>
    <span>알고리즘: <span class="val" id="infoAlgo"></span></span>
    <span>총 미션: <span class="val" id="infoMissions"></span></span>
    <span>최종 점수: <span class="val" id="infoScore"></span></span>
</div>
</div>
<div class="content-wrap">
<div class="stats" id="statsGrid"></div>
<div class="controls">
    <div class="slider-wrap">
        <label id="sliderLabel">미션 #0</label>
        <input type="range" id="timeSlider" min="0" max="0" value="0">
    </div>
    <div class="btn-group">
        <button id="btnPlay">▶ 재생</button>
        <button id="btnPause">⏸ 정지</button>
        <button id="btnStart">⏮ 처음</button>
        <button id="btnEnd">⏭ 끝</button>
        <button id="btnSpeed1" class="active">1x</button>
        <button id="btnSpeed3">3x</button>
        <button id="btnSpeed10">10x</button>
    </div>
</div>
<div class="main-layout">
    <div class="grid-panel">
        <div class="grid-container">
            <div class="out-label">◀ 출고구 (0,0)</div>
            <canvas id="gridCanvas"></canvas>
        </div>
        <div class="grid-legend">
            <span>높이 0</span>
            <div class="legend-bar" id="heightLegend"></div>
            <span id="maxHeightLabel">5</span>
        </div>
        <div class="product-legend" id="productLegend"></div>
    </div>
    <div class="chart-panel">
        <div class="chart-box"><h3>누적 이동거리</h3><canvas id="distChart" class="chart"></canvas></div>
        <div class="chart-box"><h3>재고 수량</h3><canvas id="invChart" class="chart"></canvas></div>
        <div class="chart-box"><h3>입고/출고 누적</h3><canvas id="ioChart" class="chart"></canvas></div>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<script>
const DATA = {data_json};
const PRODUCT_COLORS = {{'01':'#ff6b6b','02':'#51cf66','03':'#339af0','04':'#fcc419','05':'#cc5de8','06':'#ff922b','07':'#20c997','08':'#845ef7','default':'#868e96'}};
function productColor(n){{return PRODUCT_COLORS[n]||PRODUCT_COLORS['default'];}}
function heightColor(h,m){{if(h===0)return'rgba(240,237,233,0.7)';const t=h/m;return`rgb(${{Math.round(147-t*80)}},${{Math.round(51+t*60)}},${{Math.round(234-t*60)}})`;}}
const snaps=DATA.snapshots,COL=DATA.col,ROW=DATA.row,HEIGHT=DATA.height;
const CELL=Math.min(Math.floor(560/Math.max(COL,ROW)),28),PAD=1;
document.getElementById('infoSeed').textContent=DATA.seed.toString().padStart(6,'0');
document.getElementById('infoAlgo').textContent=DATA.algo;
document.getElementById('infoMissions').textContent=DATA.total_missions.toLocaleString();
document.getElementById('infoScore').textContent=DATA.final_score!=null?(DATA.final_score*100).toFixed(2)+'%':'-';
const lb=document.getElementById('heightLegend');document.getElementById('maxHeightLabel').textContent=HEIGHT;
for(let i=0;i<=HEIGHT;i++){{const d=document.createElement('div');d.style.background=heightColor(i,HEIGHT);lb.appendChild(d);}}
const cv=document.getElementById('gridCanvas'),cx=cv.getContext('2d');cv.width=COL*CELL+PAD*2;cv.height=ROW*CELL+PAD*2;
const sl=document.getElementById('timeSlider');sl.max=snaps.length-1;sl.addEventListener('input',()=>draw(parseInt(sl.value)));
function draw(idx){{const s=snaps[idx];if(!s)return;sl.value=idx;
document.getElementById('sliderLabel').textContent=`미션 #${{s.mission.toLocaleString()}}`;
document.getElementById('statsGrid').innerHTML=`<div class="stat-card"><div class="label">재고</div><div class="value">${{s.inv_count}}</div></div><div class="stat-card"><div class="label">입고</div><div class="value">${{s.in_count.toLocaleString()}}</div></div><div class="stat-card"><div class="label">출고</div><div class="value">${{s.out_count.toLocaleString()}}</div></div><div class="stat-card"><div class="label">누적거리</div><div class="value">${{(s.cum_dist_xy+s.cum_dist_z).toLocaleString()}}</div></div>`;
cx.fillStyle='#f4f3f0';cx.fillRect(0,0,cv.width,cv.height);
for(let x=0;x<COL;x++)for(let y=0;y<ROW;y++){{const h=s.heights[x][y],px=PAD+x*CELL,py=PAD+y*CELL;
cx.fillStyle=heightColor(h,HEIGHT);cx.fillRect(px,py,CELL-1,CELL-1);
const p=s.products[x][y];if(p&&h>0){{cx.fillStyle=productColor(p);const r=Math.max(2,CELL*.2);cx.beginPath();cx.arc(px+CELL/2-.5,py+CELL/2-.5,r,0,Math.PI*2);cx.fill();}}
if(h>0&&CELL>=16){{cx.fillStyle='rgba(0,0,0,0.7)';cx.font=`${{Math.max(8,CELL*.35)}}px sans-serif`;cx.textAlign='center';cx.textBaseline='middle';cx.fillText(h,px+CELL/2-.5,py+CELL/2-.5);}}}}
updM(idx);}}
const seenP=new Set();snaps.forEach(s=>s.products.forEach(r=>r.forEach(p=>{{if(p)seenP.add(p);}})));
const pld=document.getElementById('productLegend');Array.from(seenP).sort().forEach(p=>{{const i=document.createElement('span');i.className='item';i.innerHTML=`<span class="swatch" style="background:${{productColor(p)}}"></span>${{p}}`;pld.appendChild(i);}});
const ms=snaps.map(s=>s.mission),cd=snaps.map(s=>s.cum_dist_xy+s.cum_dist_z),iv=snaps.map(s=>s.inv_count),ic=snaps.map(s=>s.in_count),oc=snaps.map(s=>s.out_count);
const co={{responsive:true,maintainAspectRatio:false,animation:false,plugins:{{legend:{{display:false}}}},scales:{{x:{{display:true,ticks:{{color:'#9ca3af',maxTicksLimit:8,callback:v=>(v/1000).toFixed(0)+'k'}},grid:{{color:'#e5e7eb'}}}},y:{{display:true,ticks:{{color:'#9ca3af',maxTicksLimit:5}},grid:{{color:'#e5e7eb'}}}}}},elements:{{point:{{radius:0}},line:{{borderWidth:2}}}}}};
const mp={{id:'vm',afterDraw(ch){{if(ch._mi==null)return;const pt=ch.getDatasetMeta(0).data[ch._mi];if(!pt)return;const c=ch.ctx;c.save();c.strokeStyle='#dc2626';c.lineWidth=1;c.setLineDash([4,3]);c.beginPath();c.moveTo(pt.x,ch.chartArea.top);c.lineTo(pt.x,ch.chartArea.bottom);c.stroke();c.restore();}}}};
const dc=new Chart(document.getElementById('distChart'),{{type:'line',data:{{labels:ms,datasets:[{{data:cd,borderColor:'#9333ea',backgroundColor:'rgba(147,51,234,0.08)',fill:true}}]}},options:co,plugins:[mp]}});
const ivc=new Chart(document.getElementById('invChart'),{{type:'line',data:{{labels:ms,datasets:[{{data:iv,borderColor:'#9333ea',backgroundColor:'rgba(147,51,234,0.08)',fill:true}}]}},options:co,plugins:[mp]}});
const ioc=new Chart(document.getElementById('ioChart'),{{type:'line',data:{{labels:ms,datasets:[{{data:ic,borderColor:'#3b82f6',label:'입고'}},{{data:oc,borderColor:'#ef4444',label:'출고'}}]}},options:{{...co,plugins:{{legend:{{display:true,labels:{{color:'#6b7280',font:{{size:11}}}}}}}}}},plugins:[mp]}});
function updM(i){{[dc,ivc,ioc].forEach(c=>{{c._mi=i;c.update('none');}});}}
let pl=false,sp=1,af=null,lt=0;
function lp(t){{if(!pl)return;if(t-lt>100/sp){{lt=t;let i=parseInt(sl.value)+1;if(i>=snaps.length){{pl=false;return;}}draw(i);}}af=requestAnimationFrame(lp);}}
document.getElementById('btnPlay').onclick=()=>{{pl=true;af=requestAnimationFrame(lp);}};
document.getElementById('btnPause').onclick=()=>{{pl=false;if(af)cancelAnimationFrame(af);}};
document.getElementById('btnStart').onclick=()=>draw(0);
document.getElementById('btnEnd').onclick=()=>draw(snaps.length-1);
['1','3','10'].forEach(s=>{{document.getElementById('btnSpeed'+s).onclick=(e)=>{{sp=parseInt(s);document.querySelectorAll('[id^=btnSpeed]').forEach(b=>b.classList.remove('active'));e.target.classList.add('active');}};
}});
document.addEventListener('keydown',(e)=>{{if(e.key===' '){{e.preventDefault();pl?document.getElementById('btnPause').click():document.getElementById('btnPlay').click();}}else if(e.key==='ArrowLeft')draw(Math.max(0,parseInt(sl.value)-1));else if(e.key==='ArrowRight')draw(Math.min(snaps.length-1,parseInt(sl.value)+1));}});
draw(0);
</script>
</body>
</html>'''


def main():
    import datetime

    print(f"[RA viz] SEED={SEED:06d}, missions={MISSIONS:,}")
    missions = load_missions(SEED, MISSIONS)
    print(f"  미션 리스트 로드 완료: {len(missions):,}건")

    wcs = WCSMain(op_mode="n")
    wcs.mode = "RA"
    wcs.default_setting(container_name="default")

    area = wcs.WH_dict[wcs.WH_name].Zone_dict[wcs.Zone_name].Area_dict["Area_01"]
    viz = VizCollector(
        seed=SEED, algo="RA",
        col=area.COL, row=area.ROW, height=area.HEIGHT,
        total_missions=MISSIONS,
    )

    sum_dist = [0.0, 0.0]
    counts = {"IN": 0, "OUT": 0, "WAIT": 0}
    start = time.time()
    step = max(1, MISSIONS // 50)

    for i, row in enumerate(missions[:MISSIONS]):
        action = row[1]
        try:
            if action == "IN":
                moved, _ = wcs.Inbound(
                    product_name=f"{int(row[2]):02d}", DOM=row[3], testing_mode=True)
                counts["IN"] += 1
                sum_dist[0] += moved[0]; sum_dist[1] += moved[1]
            elif action == "OUT":
                moved, _ = wcs.Outbound(
                    product_name=f"{int(row[2]):02d}", testing_mode=1)
                counts["OUT"] += 1
                sum_dist[0] += moved[0]; sum_dist[1] += moved[1]
            else:
                counts["WAIT"] += 1
        except (NotEnoughSpaceError, ProductNotExistError):
            pass

        viz.collect(
            mission_num=i,
            grid=area.grid,
            product_I_dict=wcs.product_I_dict,
            cum_distance=sum_dist,
            inv_count=len(area.inventory),
            counts=counts,
        )

        if i % step == 0:
            pct = i * 100 // MISSIONS
            print(f"\r  [{'#'*(pct//4):25s}] {pct:3d}%  ({i:,}/{MISSIONS:,})  {time.time()-start:.0f}s",
                  end="", flush=True)

    elapsed = time.time() - start
    print(f"\r  [{'#'*25}] 100%  완료! ({elapsed:.1f}s)                          ")

    # 스냅샷 데이터 → JSON
    data_dict = {
        "seed":          SEED,
        "algo":          "RA",
        "col":           area.COL,
        "row":           area.ROW,
        "height":        area.HEIGHT,
        "total_missions": MISSIONS,
        "final_score":   None,
        "time_score":    None,
        "pos_score":     None,
        "snapshots":     viz.snapshots,
    }
    data_json = json.dumps(data_dict, ensure_ascii=False)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # HTML 저장
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = OUT_DIR / f"viz_RA_SEED-{SEED:06d}_{ts}.html"
    html_path.write_text(_build_light_html(data_json), encoding="utf-8")
    print(f"  HTML 저장: {html_path}")
    print(f"  스냅샷 수: {len(viz.snapshots):,}")


if __name__ == "__main__":
    main()
