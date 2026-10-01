# Source Reuse Status

## What this ZIP guarantees
1. Every externally sourced scientific parameter has a named source.
2. Public source-code repositories are linked directly.
3. The ZIP distinguishes upstream code from project-specific implementation.
4. No hypothetical EC 53 temperature curve is mislabeled as observed data.

## What this ZIP does NOT claim
It does not claim that `src/model.py` or `app.py` were copied from a published paper. They were written as project-specific integration code using the published kinetic formulation.

## If the requirement is literal source-code reuse
The next stage is to obtain the upstream repositories at fixed commits/tags, verify their licenses, and integrate only the relevant upstream modules into the computational workflow. The exact upstream commit should then be recorded in a lock file and the reused files retained with their original copyright/license notices.
