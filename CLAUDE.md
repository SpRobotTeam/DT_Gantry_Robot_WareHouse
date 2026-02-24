# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Digital Twin warehouse management system for an automated gantry robot. Manages a 20x20x5 grid-based warehouse (max 396 items) with inbound/outbound operations, Modbus TCP/IP communication to PLC, RoboDK simulation, and a Streamlit web interface. Written in Python 3.6+, all in Korean context.

## Running the System

```bash
# Install dependencies
pip install -r pip_requirements.txt

# Interactive CLI mode (press Enter at mode prompt)
python main.py

# Web interface
streamlit run WEB/web_main.py

# Simulation mode (two terminals)
python SIM/RoboDK/plc_motion006.py   # Terminal 1: RoboDK sim
python main.py                        # Terminal 2: WCS system

# Modbus test simulator (no RoboDK needed)
python MW/modbus_sim.py
```

### Operating Modes (via main.py prompt)

- **Enter**: Manual interactive mode (commands: `n`=register product, `i`=inbound, `o`=outbound, `p`=outbound by lot, `l`=list, `c`=exit)
- **`n`**: Algorithm test mode (no Modbus, requires 6-digit SEED)
- **`s`**: Benchmark evaluation mode (with scoring, requires SEED)

## Architecture

### Hierarchical Warehouse Model

```
WareHouse (WH_DT)
└── Zone (Zone_Gantry)          # Zone_mng.py - zone with Modbus interface
    ├── Area: Gantry [1×1×1]    # Robot workspace
    ├── Area: In [1×1×1]        # Inbound staging
    ├── Area: Out [1×1×1]       # Outbound staging
    └── Area: Area_01 [20×20×5] # Main storage grid
```

### Module Structure

- **`WCS/`** — Core warehouse control system
  - `SPWCS.py`: Entry class `GantryWCS` (inherits `Base_info`)
  - `Info_mng.py`: Central orchestrator `Base_info` — inherits from `product_manager`, `container_manager`, `wh_manager`. Contains `Inbound()`, `Outbound()`, `sort_item()`, `default_setting()`, `get_info()`
  - `WH_mng.py` → `Zone_mng.py` → `Area_mng.py`: Hierarchical spatial managers. Area tracks a 3D grid `grid[x][y][z]` and an `inventory` dict keyed by lot number
  - `Zone_mng.py`: Contains `optimal_pos_find()` (First-Fit or Adaptive Optimization) and Modbus communication setup

- **`MW/`** — Middleware / communication
  - `PLC_com.py`: Modbus TCP/IP server (port 502) and client classes. Data blocks for mission coordinates (from/to), gripper actions, working/ready states
  - `Product_mng.py`: Product templates (`product_manager`) and container specs (`container_manager`). Default products: '01'–'04'
  - `modbus_sim.py`: Simple register writer for testing without hardware

- **`SIM/`** — Simulation and evaluation
  - `RoboDK/plc_motion006.py`: Launches RoboDK station, handles robot motion and camera streaming (UDP 9505)
  - `EVAL/evaluator.py`: Scoring system — time score (70% weight, movement distance) + position score (30% weight, stack height uniformity)
  - `EVAL/mission_list_generator.py`: Generates randomized test missions by SEED

- **`WEB/web_main.py`** — Streamlit dashboard (port 8501) with tabs for inbound, outbound, info management, inventory, and control

- **`API/`** — Stubs only. `DB_mng.py` and `odoo_api_wrapper.py` are not yet integrated

- **`ERROR/error.py`** — Custom exceptions: `NotEnoughSpaceError`, `SimError`, `ProductNotExistError`, `DB_ObjectNotExistError`, `SIM_ObjectNotExistError`

### Key Data Structures

Product instances are tracked in `product_I_dict` (keyed by lot number):
```python
{'lot_number': {'WH_name', 'Zone_name', 'Area_name', 'product_name', 'DOM', 'loc': [x,y,z], 'height'}}
```

Area grid: `grid[x][y]` is a list (stack) of lot numbers at that column position.

### Inheritance Chain

`GantryWCS` → `Base_info` → (`product_manager` + `container_manager` + `wh_manager`)

`wh_manager` contains zones; each zone (`zone_manager`) contains areas; each area (`area_manager`) manages a grid and inventory dict.

## Network Ports

| Service | Port |
|---------|------|
| Modbus TCP | 502 (or 2502) |
| Streamlit Web UI | 8501 |
| RoboDK | 20500 |
| Camera UDP | 9505 |
| WMS (Odoo, not active) | 8069 |
| Monitoring (not active) | 8091 |

## Logging

Rotating file handlers in `logs/` (125KB max, 3 backups). Format: `{timestamp} {level} {filename}>{function} {message}`. Configured in `Logger.py`.
