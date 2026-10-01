# Version 4 Changes

- Replaced grid-based trapezoidal validation with adaptive `scipy.integrate.quad`.
- Restored multi-burst simulation in `src/multiburst.py`.
- Added stronger numerical and multi-burst tests.
- Added sensitivity plots to the Streamlit interface.
- Added `docs/FINAL_SCIENTIFIC_STATUS.md`.
- Added `docs/VALIDATION_METHOD.md`.
- Added `docs/SENSITIVITY_METHOD.md`.
- Corrected README wording so generated outputs are described as conditional on a valid input.
- Kept the EC53 temperature input empty to prevent unsupported fabricated results.
