"""
N모드 시각화 모듈
- 미션 처리 중 그리드 스냅샷 수집
- 완료 후 HTML 시각화 생성 (격자 배치 상태, 누적 이동거리 등)
- 알고리즘 비교 페이지 생성
"""
import json
import os
import glob
import datetime


class VizCollector:
    """미션 처리 중 시각화 데이터를 수집하는 클래스"""

    def __init__(self, seed, algo, col, row, height, total_missions, sample_interval=None):
        self.seed = seed
        self.algo = algo
        self.col = col
        self.row = row
        self.height = height
        self.total_missions = total_missions
        self.sample_interval = sample_interval or max(1, total_missions // 200)

        # 수집 데이터
        self.snapshots = []
        self._cum_dist = [0, 0]

    def collect(self, mission_num, grid, product_I_dict, cum_distance, inv_count, counts):
        """주기적으로 호출하여 스냅샷 수집"""
        if mission_num % self.sample_interval != 0 and mission_num != self.total_missions - 1:
            return

        heights = []
        for x in range(self.col):
            row_h = []
            for y in range(self.row):
                row_h.append(len(grid[x][y]))
            heights.append(row_h)

        products = []
        for x in range(self.col):
            row_p = []
            for y in range(self.row):
                if grid[x][y]:
                    top_lot = grid[x][y][-1]
                    info = product_I_dict.get(top_lot, {})
                    pname = info.get('product_name', '?')
                    row_p.append(pname)
                else:
                    row_p.append('')
            products.append(row_p)

        self.snapshots.append({
            'mission': mission_num,
            'heights': heights,
            'products': products,
            'cum_dist_xy': round(cum_distance[0], 1),
            'cum_dist_z': round(cum_distance[1], 1),
            'inv_count': inv_count,
            'in_count': counts.get('IN', 0),
            'out_count': counts.get('OUT', 0),
        })

    def _build_data_dict(self, final_score=None, time_score=None, pos_score=None):
        return {
            'seed': self.seed,
            'algo': self.algo,
            'col': self.col,
            'row': self.row,
            'height': self.height,
            'total_missions': self.total_missions,
            'final_score': final_score,
            'time_score': time_score,
            'pos_score': pos_score,
            'snapshots': self.snapshots,
        }

    def generate_html(self, output_dir, final_score=None, time_score=None, pos_score=None):
        """수집된 데이터로 개별 HTML + JSON 파일 생성"""
        data_dict = self._build_data_dict(final_score, time_score, pos_score)
        data_json = json.dumps(data_dict, ensure_ascii=False)

        os.makedirs(output_dir, exist_ok=True)

        # JSON 저장 (비교 페이지용, 고정 파일명)
        json_filename = f"data_{self.algo}_SEED-{self.seed:06d}.json"
        json_path = os.path.join(output_dir, json_filename)
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(data_json)

        # 개별 HTML 저장
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        html_filename = f"viz_{self.algo}_SEED-{self.seed:06d}_{timestamp}.html"
        html_path = os.path.join(output_dir, html_filename)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(_build_single_html(data_json))

        # 같은 SEED의 JSON이 2개 이상이면 비교 페이지 자동 생성
        compare_path = _try_generate_comparison(output_dir, self.seed)

        return html_path


def _try_generate_comparison(output_dir, seed):
    """같은 SEED의 JSON 파일이 여러 개 있으면 비교 HTML 생성"""
    pattern = os.path.join(output_dir, f"data_*_SEED-{seed:06d}.json")
    json_files = sorted(glob.glob(pattern))
    if len(json_files) < 2:
        return None

    datasets = []
    for jf in json_files:
        with open(jf, 'r', encoding='utf-8') as f:
            datasets.append(json.loads(f.read()))

    compare_path = os.path.join(output_dir, f"compare_SEED-{seed:06d}.html")
    all_json = json.dumps(datasets, ensure_ascii=False)
    with open(compare_path, 'w', encoding='utf-8') as f:
        f.write(_build_compare_html(all_json, seed))

    print(f"  비교 페이지 생성: {compare_path}")
    return compare_path


def _build_compare_html(all_data_json, seed):
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>알고리즘 비교 - SEED {seed:06d}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; padding: 15px; }}
h1 {{ text-align: center; margin-bottom: 5px; font-size: 1.4em; color: #00d2ff; }}
.subtitle {{ text-align: center; color: #666; font-size: 0.85em; margin-bottom: 15px; }}

.controls {{ text-align: center; margin: 12px 0; }}
.slider-wrap {{ display: flex; align-items: center; gap: 10px; max-width: 800px; margin: 0 auto; }}
.slider-wrap input[type=range] {{ flex: 1; accent-color: #00d2ff; }}
.slider-wrap label {{ font-size: 0.9em; min-width: 180px; color: #ccc; }}
.btn-group {{ margin-top: 8px; }}
.btn-group button {{ background: #16213e; color: #00d2ff; border: 1px solid #00d2ff44; padding: 5px 16px;
    border-radius: 4px; cursor: pointer; margin: 0 3px; font-size: 0.8em; }}
.btn-group button:hover {{ background: #0f3460; }}
.btn-group button.active {{ background: #00d2ff; color: #1a1a2e; }}

.grids-row {{ display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; margin-bottom: 15px; }}
.algo-col {{ text-align: center; }}
.algo-title {{ font-size: 1.1em; font-weight: bold; margin-bottom: 6px; }}
.algo-title.ff {{ color: #868e96; }}
.algo-title.rl {{ color: #51cf66; }}
.algo-title.la {{ color: #fcc419; }}
.algo-title.ao {{ color: #cc5de8; }}

.algo-stats {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 4px; margin-top: 6px; font-size: 0.75em; }}
.algo-stats .s {{ background: #16213e; border-radius: 4px; padding: 4px 8px; }}
.algo-stats .s .lbl {{ color: #666; }}
.algo-stats .s .val {{ color: #00d2ff; font-weight: bold; }}

canvas.grid {{ border: 1px solid #333; border-radius: 6px; }}
.out-arrow {{ font-size: 0.65em; color: #ff6b6b; margin-bottom: 2px; }}

.legend-row {{ display: flex; justify-content: center; gap: 20px; margin: 8px 0; font-size: 0.75em; }}
.legend-row .h-bar {{ display: flex; height: 14px; width: 120px; border-radius: 3px; overflow: hidden; }}
.legend-row .h-bar div {{ flex: 1; }}
.legend-row .p-item {{ display: flex; align-items: center; gap: 3px; }}
.legend-row .p-swatch {{ width: 12px; height: 12px; border-radius: 2px; border: 1px solid #555; }}

/* Comparison chart */
.chart-section {{ max-width: 900px; margin: 0 auto; }}
.chart-box {{ background: #16213e; border-radius: 8px; padding: 15px; margin-bottom: 12px; }}
.chart-box h3 {{ font-size: 0.85em; color: #888; margin-bottom: 8px; }}
canvas.chart {{ width: 100% !important; height: 200px !important; }}

/* Score comparison */
.score-row {{ display: flex; justify-content: center; gap: 20px; margin: 10px 0; }}
.score-card {{ background: #16213e; border-radius: 8px; padding: 15px 25px; text-align: center; min-width: 140px; }}
.score-card .algo-name {{ font-size: 0.8em; color: #888; margin-bottom: 4px; }}
.score-card .total-dist {{ font-size: 1.4em; font-weight: bold; color: #00d2ff; }}
.score-card .reduction {{ font-size: 0.8em; color: #51cf66; margin-top: 2px; }}
</style>
</head>
<body>

<h1>알고리즘 배치 비교</h1>
<div class="subtitle">SEED {seed:06d} | 동일 미션 리스트 기준</div>

<div class="score-row" id="scoreRow"></div>

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

<div class="legend-row">
    <span>높이: 0</span>
    <div class="h-bar" id="hLegend"></div>
    <span id="maxHLabel">5</span>
    <span style="margin-left:15px;">제품:</span>
    <span id="pLegend"></span>
</div>

<div class="grids-row" id="gridsRow"></div>

<div class="chart-section">
    <div class="chart-box">
        <h3>누적 이동거리 비교</h3>
        <canvas id="distChart" class="chart"></canvas>
    </div>
    <div class="chart-box">
        <h3>재고 수량 비교</h3>
        <canvas id="invChart" class="chart"></canvas>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<script>
const ALL = {all_data_json};

const ALGO_COLORS = {{
    'FF': '#868e96', 'RL': '#51cf66', 'LA': '#fcc419', 'AO': '#cc5de8'
}};
const PRODUCT_COLORS = {{
    '01': '#ff6b6b', '02': '#51cf66', '03': '#339af0', '04': '#fcc419',
    '05': '#cc5de8', '06': '#ff922b', '07': '#20c997', '08': '#845ef7',
    'default': '#868e96'
}};
function productColor(n) {{ return PRODUCT_COLORS[n] || PRODUCT_COLORS['default']; }}
function heightColor(h, maxH) {{
    if (h === 0) return 'rgba(22,33,62,0.5)';
    const t = h / maxH;
    return `rgb(${{Math.round(t*0)}},${{Math.round(40+t*170)}},${{Math.round(80+t*175)}})`;
}}

const COL = ALL[0].col, ROW = ALL[0].row, HEIGHT = ALL[0].height;
const CELL = Math.min(Math.floor(480 / Math.max(COL, ROW)), 24);
const PAD = 1;
const CW = COL * CELL + PAD * 2;
const CH = ROW * CELL + PAD * 2;

// Max snapshot count (use minimum across all datasets for sync)
const maxSnaps = Math.min(...ALL.map(d => d.snapshots.length));

// Score cards
const scoreRow = document.getElementById('scoreRow');
const ffData = ALL.find(d => d.algo === 'FF');
ALL.forEach(d => {{
    const last = d.snapshots[d.snapshots.length - 1];
    const totalDist = last.cum_dist_xy + last.cum_dist_z;
    const card = document.createElement('div');
    card.className = 'score-card';
    let reductionHtml = '';
    if (ffData && d.algo !== 'FF') {{
        const ffLast = ffData.snapshots[ffData.snapshots.length - 1];
        const ffDist = ffLast.cum_dist_xy + ffLast.cum_dist_z;
        const pct = ((ffDist - totalDist) / ffDist * 100).toFixed(1);
        reductionHtml = `<div class="reduction">FF 대비 -${{pct}}%</div>`;
    }}
    card.innerHTML = `
        <div class="algo-name" style="color:${{ALGO_COLORS[d.algo] || '#aaa'}}">${{d.algo}}</div>
        <div class="total-dist">${{Math.round(totalDist).toLocaleString()}}</div>
        ${{reductionHtml}}
    `;
    scoreRow.appendChild(card);
}});

// Height legend
const hLeg = document.getElementById('hLegend');
document.getElementById('maxHLabel').textContent = HEIGHT;
for (let i = 0; i <= HEIGHT; i++) {{
    const d = document.createElement('div');
    d.style.background = heightColor(i, HEIGHT);
    hLeg.appendChild(d);
}}

// Product legend
const seenP = new Set();
ALL.forEach(d => d.snapshots.forEach(s => s.products.forEach(r => r.forEach(p => {{ if(p) seenP.add(p); }}))));
const pLeg = document.getElementById('pLegend');
Array.from(seenP).sort().forEach(p => {{
    const sp = document.createElement('span');
    sp.className = 'p-item';
    sp.innerHTML = `<span class="p-swatch" style="background:${{productColor(p)}}"></span>${{p}}`;
    pLeg.appendChild(sp);
}});

// Create grid canvases
const gridsRow = document.getElementById('gridsRow');
const contexts = [];
ALL.forEach((d, i) => {{
    const col = document.createElement('div');
    col.className = 'algo-col';
    col.innerHTML = `
        <div class="algo-title ${{d.algo.toLowerCase()}}">${{d.algo}}</div>
        <div class="out-arrow">◀ 출고구 (0,0)</div>
        <canvas class="grid" id="grid${{i}}" width="${{CW}}" height="${{CH}}"></canvas>
        <div class="algo-stats" id="stats${{i}}"></div>
    `;
    gridsRow.appendChild(col);
    contexts.push(document.getElementById('grid' + i).getContext('2d'));
}});

// Slider
const slider = document.getElementById('timeSlider');
slider.max = maxSnaps - 1;
slider.addEventListener('input', () => drawAll(parseInt(slider.value)));

function drawAll(idx) {{
    slider.value = idx;
    const refSnap = ALL[0].snapshots[idx];
    if (!refSnap) return;
    document.getElementById('sliderLabel').textContent = `미션 #${{refSnap.mission.toLocaleString()}}`;

    ALL.forEach((d, i) => {{
        const snap = d.snapshots[idx];
        if (!snap) return;
        const ctx = contexts[i];

        // Stats
        document.getElementById('stats' + i).innerHTML = `
            <div class="s"><span class="lbl">재고</span> <span class="val">${{snap.inv_count}}</span></div>
            <div class="s"><span class="lbl">거리</span> <span class="val">${{Math.round(snap.cum_dist_xy + snap.cum_dist_z).toLocaleString()}}</span></div>
            <div class="s"><span class="lbl">입고</span> <span class="val">${{snap.in_count.toLocaleString()}}</span></div>
            <div class="s"><span class="lbl">출고</span> <span class="val">${{snap.out_count.toLocaleString()}}</span></div>
        `;

        // Grid
        ctx.fillStyle = '#0f0f23';
        ctx.fillRect(0, 0, CW, CH);
        for (let x = 0; x < COL; x++) {{
            for (let y = 0; y < ROW; y++) {{
                const h = snap.heights[x][y];
                const px = PAD + x * CELL, py = PAD + y * CELL;
                ctx.fillStyle = heightColor(h, HEIGHT);
                ctx.fillRect(px, py, CELL - 1, CELL - 1);
                const pn = snap.products[x][y];
                if (pn && h > 0) {{
                    ctx.fillStyle = productColor(pn);
                    const r = Math.max(2, CELL * 0.2);
                    ctx.beginPath();
                    ctx.arc(px + CELL/2 - .5, py + CELL/2 - .5, r, 0, Math.PI*2);
                    ctx.fill();
                }}
                if (h > 0 && CELL >= 14) {{
                    ctx.fillStyle = '#fff';
                    ctx.font = `${{Math.max(7, CELL*0.35)}}px sans-serif`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(h, px + CELL/2 - .5, py + CELL/2 - .5);
                }}
            }}
        }}
    }});
    updateChartMarkers(idx);
}}

// Charts
const chartOpts = {{
    responsive: true, maintainAspectRatio: false, animation: false,
    plugins: {{ legend: {{ display: true, labels: {{ color: '#aaa', font: {{ size: 11 }} }} }} }},
    scales: {{
        x: {{ display: true, ticks: {{ color: '#666', maxTicksLimit: 8, callback: v => (v/1000).toFixed(0)+'k' }}, grid: {{ color: '#222' }} }},
        y: {{ display: true, ticks: {{ color: '#666', maxTicksLimit: 5 }}, grid: {{ color: '#222' }} }}
    }},
    elements: {{ point: {{ radius: 0 }}, line: {{ borderWidth: 2 }} }}
}};
const markerPlugin = {{
    id: 'vMarker',
    afterDraw(chart) {{
        if (chart._mIdx == null) return;
        const pt = chart.getDatasetMeta(0).data[chart._mIdx];
        if (!pt) return;
        const c = chart.ctx;
        c.save(); c.strokeStyle = '#ff6b6b'; c.lineWidth = 1; c.setLineDash([4,3]);
        c.beginPath(); c.moveTo(pt.x, chart.chartArea.top); c.lineTo(pt.x, chart.chartArea.bottom); c.stroke();
        c.restore();
    }}
}};

const missions = ALL[0].snapshots.slice(0, maxSnaps).map(s => s.mission);

const distChart = new Chart(document.getElementById('distChart'), {{
    type: 'line',
    data: {{ labels: missions, datasets: ALL.map(d => ({{
        label: d.algo,
        data: d.snapshots.slice(0, maxSnaps).map(s => s.cum_dist_xy + s.cum_dist_z),
        borderColor: ALGO_COLORS[d.algo] || '#aaa',
        backgroundColor: 'transparent'
    }})) }},
    options: chartOpts, plugins: [markerPlugin]
}});

const invChart = new Chart(document.getElementById('invChart'), {{
    type: 'line',
    data: {{ labels: missions, datasets: ALL.map(d => ({{
        label: d.algo,
        data: d.snapshots.slice(0, maxSnaps).map(s => s.inv_count),
        borderColor: ALGO_COLORS[d.algo] || '#aaa',
        backgroundColor: 'transparent'
    }})) }},
    options: chartOpts, plugins: [markerPlugin]
}});

function updateChartMarkers(idx) {{
    [distChart, invChart].forEach(c => {{ c._mIdx = idx; c.update('none'); }});
}}

// Playback
let playing = false, speed = 1, anim = null, lastT = 0;
function loop(ts) {{
    if (!playing) return;
    if (ts - lastT > 100 / speed) {{ lastT = ts; let i = parseInt(slider.value)+1; if (i >= maxSnaps) {{ playing = false; return; }} drawAll(i); }}
    anim = requestAnimationFrame(loop);
}}
document.getElementById('btnPlay').onclick = () => {{ playing = true; anim = requestAnimationFrame(loop); }};
document.getElementById('btnPause').onclick = () => {{ playing = false; if(anim) cancelAnimationFrame(anim); }};
document.getElementById('btnStart').onclick = () => drawAll(0);
document.getElementById('btnEnd').onclick = () => drawAll(maxSnaps - 1);
['1','3','10'].forEach(s => {{
    document.getElementById('btnSpeed'+s).onclick = (e) => {{
        speed = parseInt(s);
        document.querySelectorAll('[id^=btnSpeed]').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
    }};
}});
document.addEventListener('keydown', (e) => {{
    if (e.key === ' ') {{ e.preventDefault(); playing ? document.getElementById('btnPause').click() : document.getElementById('btnPlay').click(); }}
    else if (e.key === 'ArrowLeft') drawAll(Math.max(0, parseInt(slider.value)-1));
    else if (e.key === 'ArrowRight') drawAll(Math.min(maxSnaps-1, parseInt(slider.value)+1));
}});

drawAll(0);
</script>
</body>
</html>'''


def _build_single_html(data_json):
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>창고 배치 시각화</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }}
h1 {{ text-align: center; margin-bottom: 10px; font-size: 1.5em; color: #00d2ff; }}
.info-bar {{ display: flex; justify-content: center; gap: 30px; margin-bottom: 15px; font-size: 0.9em; color: #aaa; }}
.info-bar span {{ background: #16213e; padding: 5px 15px; border-radius: 20px; }}
.info-bar .val {{ color: #00d2ff; font-weight: bold; }}
.main-layout {{ display: flex; gap: 20px; max-width: 1400px; margin: 0 auto; }}
.grid-panel {{ flex: 0 0 auto; }}
.chart-panel {{ flex: 1; min-width: 300px; }}
.grid-container {{ position: relative; }}
canvas#gridCanvas {{ border: 1px solid #333; border-radius: 8px; }}
.grid-legend {{ display: flex; align-items: center; gap: 10px; margin-top: 8px; font-size: 0.75em; }}
.legend-bar {{ display: flex; height: 16px; border-radius: 3px; overflow: hidden; flex: 1; }}
.legend-bar div {{ flex: 1; }}
.controls {{ text-align: center; margin: 15px 0; }}
.slider-wrap {{ display: flex; align-items: center; gap: 10px; max-width: 700px; margin: 0 auto; }}
.slider-wrap input[type=range] {{ flex: 1; accent-color: #00d2ff; }}
.slider-wrap label {{ font-size: 0.85em; min-width: 150px; color: #aaa; }}
.btn-group {{ margin-top: 8px; }}
.btn-group button {{ background: #16213e; color: #00d2ff; border: 1px solid #00d2ff44; padding: 6px 18px;
    border-radius: 4px; cursor: pointer; margin: 0 4px; font-size: 0.85em; }}
.btn-group button:hover {{ background: #0f3460; }}
.btn-group button.active {{ background: #00d2ff; color: #1a1a2e; }}
.stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 15px; }}
.stat-card {{ background: #16213e; border-radius: 8px; padding: 12px; text-align: center; }}
.stat-card .label {{ font-size: 0.75em; color: #888; }}
.stat-card .value {{ font-size: 1.3em; font-weight: bold; color: #00d2ff; margin-top: 4px; }}
.chart-box {{ background: #16213e; border-radius: 8px; padding: 15px; margin-bottom: 15px; }}
.chart-box h3 {{ font-size: 0.9em; color: #888; margin-bottom: 10px; }}
canvas.chart {{ width: 100% !important; height: 180px !important; }}
.product-legend {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; font-size: 0.75em; }}
.product-legend .item {{ display: flex; align-items: center; gap: 4px; }}
.product-legend .swatch {{ width: 14px; height: 14px; border-radius: 3px; border: 1px solid #555; }}
.out-label {{ position: absolute; top: -22px; left: 0; font-size: 0.7em; color: #ff6b6b; }}
</style>
</head>
<body>
<h1>창고 격자 배치 시각화</h1>
<div class="info-bar">
    <span>SEED: <span class="val" id="infoSeed"></span></span>
    <span>알고리즘: <span class="val" id="infoAlgo"></span></span>
    <span>총 미션: <span class="val" id="infoMissions"></span></span>
    <span>최종 점수: <span class="val" id="infoScore"></span></span>
</div>
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
function heightColor(h,m){{if(h===0)return'rgba(22,33,62,0.5)';const t=h/m;return`rgb(${{Math.round(t*0)}},${{Math.round(40+t*170)}},${{Math.round(80+t*175)}})`;}}
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
cx.fillStyle='#0f0f23';cx.fillRect(0,0,cv.width,cv.height);
for(let x=0;x<COL;x++)for(let y=0;y<ROW;y++){{const h=s.heights[x][y],px=PAD+x*CELL,py=PAD+y*CELL;
cx.fillStyle=heightColor(h,HEIGHT);cx.fillRect(px,py,CELL-1,CELL-1);
const p=s.products[x][y];if(p&&h>0){{cx.fillStyle=productColor(p);const r=Math.max(2,CELL*.2);cx.beginPath();cx.arc(px+CELL/2-.5,py+CELL/2-.5,r,0,Math.PI*2);cx.fill();}}
if(h>0&&CELL>=16){{cx.fillStyle='#fff';cx.font=`${{Math.max(8,CELL*.35)}}px sans-serif`;cx.textAlign='center';cx.textBaseline='middle';cx.fillText(h,px+CELL/2-.5,py+CELL/2-.5);}}}}
updM(idx);}}
const seenP=new Set();snaps.forEach(s=>s.products.forEach(r=>r.forEach(p=>{{if(p)seenP.add(p);}})));
const pld=document.getElementById('productLegend');Array.from(seenP).sort().forEach(p=>{{const i=document.createElement('span');i.className='item';i.innerHTML=`<span class="swatch" style="background:${{productColor(p)}}"></span>${{p}}`;pld.appendChild(i);}});
const ms=snaps.map(s=>s.mission),cd=snaps.map(s=>s.cum_dist_xy+s.cum_dist_z),iv=snaps.map(s=>s.inv_count),ic=snaps.map(s=>s.in_count),oc=snaps.map(s=>s.out_count);
const co={{responsive:true,maintainAspectRatio:false,animation:false,plugins:{{legend:{{display:false}}}},scales:{{x:{{display:true,ticks:{{color:'#666',maxTicksLimit:8,callback:v=>(v/1000).toFixed(0)+'k'}},grid:{{color:'#222'}}}},y:{{display:true,ticks:{{color:'#666',maxTicksLimit:5}},grid:{{color:'#222'}}}}}},elements:{{point:{{radius:0}},line:{{borderWidth:2}}}}}};
const mp={{id:'vm',afterDraw(ch){{if(ch._mi==null)return;const pt=ch.getDatasetMeta(0).data[ch._mi];if(!pt)return;const c=ch.ctx;c.save();c.strokeStyle='#ff6b6b';c.lineWidth=1;c.setLineDash([4,3]);c.beginPath();c.moveTo(pt.x,ch.chartArea.top);c.lineTo(pt.x,ch.chartArea.bottom);c.stroke();c.restore();}}}};
const dc=new Chart(document.getElementById('distChart'),{{type:'line',data:{{labels:ms,datasets:[{{data:cd,borderColor:'#00d2ff',backgroundColor:'rgba(0,210,255,0.1)',fill:true}}]}},options:co,plugins:[mp]}});
const ivc=new Chart(document.getElementById('invChart'),{{type:'line',data:{{labels:ms,datasets:[{{data:iv,borderColor:'#51cf66',backgroundColor:'rgba(81,207,102,0.1)',fill:true}}]}},options:co,plugins:[mp]}});
const ioc=new Chart(document.getElementById('ioChart'),{{type:'line',data:{{labels:ms,datasets:[{{data:ic,borderColor:'#339af0',label:'입고'}},{{data:oc,borderColor:'#ff6b6b',label:'출고'}}]}},options:{{...co,plugins:{{legend:{{display:true,labels:{{color:'#aaa',font:{{size:11}}}}}}}}}},plugins:[mp]}});
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
