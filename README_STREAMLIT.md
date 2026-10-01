# EC 53 Forsterite Crystallization — Streamlit System

## Research title

**Time-Dependent Forsterite Crystallization During Protostellar Accretion Bursts: Modeling Non-Isothermal Kinetics**

## What this application does

This application provides a browser-based interface for the source-grounded computational model in this repository. It accepts a time-dependent temperature history `T(t)`, evaluates the Arrhenius crystallization rate, solves the time-dependent crystallinity equation with RK45, independently checks the result with quadrature, and presents graphs, numerical results, sensitivity analysis, and downloadable data.

The core equations are:

\[
k(T)=\nu\exp[-(E_a/k_B)/T]
\]

and

\[
\frac{dX}{dt}=k(T(t))(1-X)
\]

where `X` is the crystalline fraction.

## Important scientific rule

The application **does not fabricate an EC 53 temperature curve**. The project input file is intentionally empty until a defensible source/model-derived temperature history is supplied.

A CSV supplied to the application becomes an input to the kinetic calculation. It must not be described as an observed EC 53 dust temperature unless its provenance supports that statement.

## How to run

### Windows — easiest method

Double-click:

```text
run_app.bat
```

The script installs the required packages and launches Streamlit.

### Command line

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate
```

Install dependencies:

```bash
python -m pip install -r requirements-app.txt
```

Start the application:

```bash
python -m streamlit run app.py
```

A browser window will open at the local Streamlit address.

## User workflow

1. Open the application.
2. Upload a CSV containing `time_s` and `temperature_K`.
3. Review the temperature plot and input table.
4. Set initial crystallinity if appropriate.
5. Keep the documented literature-based kinetic parameters unless a justified research analysis requires alternatives.
6. Click **Run simulation**.
7. Inspect the three graphs.
8. Inspect the independent RK45-versus-quadrature validation.
9. Run sensitivity analysis if needed.
10. Download the simulation CSV and summary JSON.

## Required input format

```csv
time_s,temperature_K
0,300
3600,420
7200,550
...
```

The example values above are only a format illustration. They must **not** be treated as EC 53 measurements.

Requirements:

- at least two rows;
- `time_s` strictly increasing;
- `temperature_K` strictly positive;
- numeric values only.

## Interface sections

### Main simulation

Shows:

- number of input points;
- simulation duration;
- minimum and maximum temperature;
- temperature history;
- final crystallinity;
- maximum crystallization rate;
- validation error.

### Graphs

Produces:

- Temperature vs time;
- Crystallization rate vs time;
- Crystalline fraction vs time.

### Validation

The model solves the ODE numerically with SciPy RK45. It also evaluates the equivalent integrated form using numerical quadrature. The maximum absolute difference is reported as an internal numerical consistency check.

### Sensitivity

The application supports one-factor-at-a-time computational sensitivity tests for:

- temperature multiplier;
- kinetic prefactor `ν` multiplier;
- activation parameter `Ea/kB` multiplier.

These are **model sensitivity experiments**, not measurements or uncertainty estimates unless an uncertainty methodology is added separately.

### Data & provenance

The application explicitly displays the source label, model equation, kinetic parameters, and numerical solver.

## Project structure

```text
EC53_forsterite_source_grounded_final/
├── app.py
├── run_app.bat
├── requirements.txt
├── requirements-app.txt
├── README.md
├── README_STREAMLIT.md
├── EXTERNAL_DATA_MANIFEST.csv
├── input/
│   ├── README.md
│   └── ec53_temperature_history.csv
├── src/
│   ├── model.py
│   ├── io.py
│   ├── plotting.py
│   └── run_final.py
├── tests/
│   └── test_model.py
├── docs/
│   ├── ASSUMPTION_LEDGER.md
│   ├── EC53_SOURCE_INPUTS.csv
│   ├── SOURCES.md
│   └── TEMPERATURE_PROVENANCE.md
└── scripts/
    ├── check_provenance.py
    └── run_tests.py
```

## Scientific provenance

The underlying package documents EC 53 observational context and external scientific sources in `docs/SOURCES.md`, `docs/SOURCE_URLS.txt`, and `docs/TEMPERATURE_PROVENANCE.md`.

The application itself does not turn a model assumption into an observation. The temperature history is therefore a required external input for an EC 53-specific scientific result.

## What counts as a final research result?

A defensible final EC 53 result requires:

1. a documented temperature history or temperature field derived from a defensible physical model or public observational/model data;
2. documented provenance for that input;
3. literature-supported kinetic parameters;
4. a reproducible numerical calculation;
5. validation of the numerical implementation;
6. sensitivity/uncertainty analysis appropriate to the research question.

The Streamlit interface is the presentation and reproducibility layer; it does not replace these scientific requirements.
