# GeracaoMartece-IC

🌐 **[Ler em português](README.md)**

Undergraduate research project (Iniciação Científica) in computational astrophysics: modeling the coupling between the solar wind and Earth's magnetosphere and its relationship to the occurrence of auroras.

🔗 **Live site:** https://geracao-martece-ic.vercel.app

## About the project

We investigate how solar wind energy is transferred into Earth's magnetosphere during geomagnetic storms, using classic coupling functions from the literature (Akasofu, 1981; Newell et al., 2007) integrated with the empirical Burton et al. (1975) ring-current equation via 4th-order Runge-Kutta.

The core of the work is honest statistical validation: instead of fitting the model and measuring error on the same data (retrospective fitting), we calibrate each event using only the first 60% of its time window and measure the error (RMSE) on the final 40% — data the optimizer never saw. This genuine holdout protocol was replicated across five historical geomagnetic storms of very different intensities:

- Halloween Storm (Oct/2003)
- Aug/2011 storm
- St. Patrick's Day Storm (Mar/2015)
- Sep/2017 storm
- Gannon Storm (May/2024)

We also evaluated the correlation between the coupling rate and the AE index (auroral electrojet) pooled across all five events, and estimated the latitudinal expansion of the auroral oval from a Kp value derived from the modeled Dst.

## Repository structure

```
geracaomartece-ic/
├── python/          # Scientific pipeline: ingestion, coupling, RK4 solver, calibration, forecasting, aurora
├── backend/         # FastAPI serving pre-computed results (resultados.json) to the frontend
├── frontend/        # Vue 3 + Three.js + Chart.js site, with native PT/EN i18n
├── core/            # Experimental Rust core (ode_solvers) — work in progress
├── notebooks/       # Jupyter notebooks with the full pipeline and data exploration
└── tests/           # Automated tests (pytest) for the Python pipeline
```

## Data

Solar wind, interplanetary magnetic field (IMF) and geomagnetic index (Dst, AE, Kp) data come from the **OMNI** database (NASA GSFC/SPDF), fetched at 1-minute resolution via `pyspedas`.

## Technologies

**Science & computation**
- Python — NumPy, Pandas, SciPy (`differential_evolution` for global calibration)
- Fixed-step (60s) 4th-order Runge-Kutta solver
- pytest for automated testing

**Backend**
- FastAPI serving pre-processed results

**Frontend**
- Vue 3 (`<script setup>`)
- Three.js — 3D auroral oval scene
- Chart.js — Dst time series
- Native i18n (PT/EN), no external library
- Deployed via Vercel

## How to run

### Backend

```powershell
cd backend
pip install fastapi uvicorn
uvicorn main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Tests

```powershell
pip install pytest
pytest tests/
```

## Authors

- Guilherme Savassa Bernal
- Luiny Beatriz dos Santos Pinto

Advisor: Clari

## License

See [LICENSE](LICENSE).
