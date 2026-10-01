# EC 53 Source-Grounded Forsterite Crystallization Simulation

## Purpose

This package models time-dependent forsterite crystallization during an EC 53 accretion-burst context using:

1. Published EC 53 observational constraints;
2. Published laboratory/astrophysical crystallization kinetics;
3. A transparent numerical implementation written for this project;
4. A user-supplied temperature history `input/ec53_temperature_history.csv`.

The package intentionally DOES NOT invent an EC 53 temperature curve.

## Scientific status

This is a reproducible computational framework. A publication-quality EC 53 result
requires a defensible `T(t)` or `T(r,t)` derived from published modelling or from
public JWST/ALMA data plus a documented radiative-transfer model.

The current package therefore separates:

- SOURCE-CONSTRAINED INPUTS: literature-derived quantities;
- DERIVED QUANTITIES: values calculated by this code;
- USER/PHYSICAL-MODEL INPUTS: quantities that must be supplied from an external
  temperature model.

## Key published constraints

EC 53:
- Recurrence/cycle: approximately 530 days;
- Rapid rise: approximately 0.12 yr;
- Decay e-folding time: approximately 0.74 yr;
- Outburst luminosity approximately 3.3 times quiescent luminosity;
- Peak accretion rate approximately 8e-6 Msun/yr.

Sources:
- Lee et al. 2020, arXiv:2009.05268
- Baek et al. 2020, arXiv:2004.05600
- Lee et al. 2026, Nature 649, 853-858, DOI: 10.1038/s41586-025-09939-3

The 2026 Nature paper reports burst-only forsterite and enstatite emission and
states that the JWST MIRI/NIRCam and ALMA data are publicly available.

## Kinetic model

Arrhenius rate:

k(T) = nu * exp[-(Ea/kB)/T]

Crystalline fraction:

dX/dt = k(T) * (1 - X)

where X is the crystalline fraction from 0 to 1.

Kinetic constants used in the default configuration:
- nu = 2.0e13 s^-1
- Ea/kB = 39100 K

These are literature-based, not fitted by this package.

## What is NOT hard-coded

The following are intentionally not treated as measured EC 53 values:

- absolute dust temperature;
- a 950 K peak temperature;
- a 12-hour burst duration;
- a sin^2 temperature profile.

If `input/ec53_temperature_history.csv` is empty, the main run stops with an
explicit error instead of generating a fabricated result.

## Run

```bash
python -m pip install -r requirements.txt
python -m src.run_final
```

Run tests:

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

## Input format

`input/ec53_temperature_history.csv`

```csv
time_s,temperature_K
0,300
...
```

The temperature history may come from:
- a published EC 53 radiative-transfer model;
- a documented RADMC-3D calculation;
- a processed observational/model product.

The provenance of the temperature file must be documented in
`docs/TEMPERATURE_PROVENANCE.md`.

## Outputs

When a valid temperature-history input is supplied and the model is run, outputs can include:
- `results/baseline_timeseries.csv`
- `results/baseline_summary.json`
- temperature/rate/crystallinity figures
- validation results
- multi-burst results
- sensitivity tables and figures

The source distribution does **not** contain a fabricated EC 53 result. No scientific output is presented as an EC 53 observation.

## External software

- Python
- NumPy
- SciPy
- Pandas
- Matplotlib
- Astropy (optional, for FITS/MAST workflows)
- JWST pipeline / RADMC-3D are external tools and are not bundled here.

## Reproducibility principle

Every parameter must be assigned one of:
SOURCE, DERIVED, MODEL INPUT, or NUMERICAL SETTING.

See `docs/ASSUMPTION_LEDGER.md`.

## Streamlit application

A browser-based research interface is included in `app.py`.

Install:

```bash
python -m pip install -r requirements-app.txt
```

Run:

```bash
python -m streamlit run app.py
```

See `README_STREAMLIT.md` for the complete user workflow.

## Version 4 scientific updates

Version 4 adds adaptive `scipy.integrate.quad` validation, multi-burst orchestration, stronger tests, sensitivity plots, and explicit final scientific-status documentation. It still refuses to invent an EC 53 temperature history.

## Source-transparent version
This distribution includes `docs/SOURCE_CODE_MAP.md`, `docs/PARAMETER_PROVENANCE.csv`, `docs/DATA_PROVENANCE.csv`, `docs/MODIFICATIONS.md`, and `SOURCE_REUSE_STATUS.md`. These files identify where externally sourced code/data/parameters come from and clearly distinguish them from project-specific integration code.
