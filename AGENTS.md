# Repository Guidelines

## Project Structure & Module Organization
- `main.py`: Primary entry point for CLI/manual mode, algorithm test mode (`N`), and benchmark mode (`S`).
- `WCS/`: Core warehouse control logic (`SPWCS.py`, `Info_mng.py`, `WH_mng.py`, `Zone_mng.py`, `Area_mng.py`).
- `MW/`: Middleware and device communication (`PLC_com.py`, `modbus_sim.py`, product/container managers).
- `SIM/`: Simulation and evaluation tools.
  - `SIM/RoboDK/`: RoboDK station and motion scripts.
  - `SIM/EVAL/`: mission generation, scoring, and visualization.
- `WEB/web_main.py`: Streamlit UI.
- `ERROR/error.py`: Domain exceptions.
- `docs/` and `doc/`: generated reports and reference materials.

## Build, Test, and Development Commands
- `pip install -r pip_requirements.txt`: install runtime dependencies.
- `python main.py`: run the WCS CLI (manual mode when pressing Enter at the mode prompt).
- `streamlit run WEB/web_main.py`: launch the web interface on port `8501`.
- `python MW/modbus_sim.py`: run Modbus simulator for communication checks.
- `python SIM/RoboDK/plc_motion006.py`: start RoboDK-side simulation process.

## Coding Style & Naming Conventions
- Target Python `3.6+`; use 4-space indentation and keep lines readable.
- Follow current naming patterns:
  - Classes: `PascalCase` (for example, `GantryWCS`, `Evaluator`).
  - Functions/variables: `snake_case`.
  - Existing module filenames use project-specific suffixes (for example, `*_mng.py`); preserve these patterns in touched areas.
- Prefer small, focused edits and reuse existing manager layers (`Area -> Zone -> WH`) instead of bypassing abstractions.

## Testing Guidelines
- No formal unit-test suite is enforced yet. Use reproducible scenario checks:
  - CLI smoke test via `python main.py`.
  - Algorithm/evaluation runs in `N`/`S` mode with a fixed 6-digit seed (for example, `123456`).
  - Web smoke test via `streamlit run WEB/web_main.py`.
- Validate outputs in `logs/` and, for algorithm runs, generated artifacts in `docs/viz/`.

## Commit & Pull Request Guidelines
- Recent history favors short, imperative subjects, sometimes with prefixes (`docs:`, `Fix`, `Add`) and sometimes date-style Korean messages. Keep subjects concise and specific.
- Recommended format: `type: summary` (for example, `fix: handle empty inventory in outbound path`).
- PRs should include:
  - What changed and why.
  - How it was tested (exact commands, seeds, mode).
  - Screenshots for UI changes (`WEB/`) and sample output paths for visualization/report changes.

## Security & Configuration Tips
- Use `.env.example` as a template; never commit secrets or local credentials.
- Keep local logs and temporary artifacts out of commits unless they are intentional documentation outputs.
