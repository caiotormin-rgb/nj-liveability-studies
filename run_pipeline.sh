#!/usr/bin/env bash
# run_pipeline.sh — run the NJ pipeline with pre-flight checks
set -euo pipefail

DB_PATH="$(dirname "$0")/data/db/nj_pipeline.duckdb"
CONDA_ENV="nj-pipeline"
SCRIPT="pipeline/run_all.py"

# ── helpers ──────────────────────────────────────────────────────────────────
log()  { echo "[$(date '+%H:%M:%S')] $*"; }
err()  { echo "[$(date '+%H:%M:%S')] ERROR: $*" >&2; }
die()  { err "$*"; exit 1; }

# ── 1. locate conda ───────────────────────────────────────────────────────────
if command -v conda &>/dev/null; then
    CONDA_BASE="$(conda info --base 2>/dev/null)"
elif [ -f "$HOME/opt/anaconda3/etc/profile.d/conda.sh" ]; then
    CONDA_BASE="$HOME/opt/anaconda3"
elif [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
    CONDA_BASE="/opt/anaconda3"
else
    die "conda not found. Install Anaconda/Miniconda or add it to PATH."
fi

PYTHON="$CONDA_BASE/envs/$CONDA_ENV/bin/python"
[ -x "$PYTHON" ] || die "Conda env '$CONDA_ENV' not found at $CONDA_BASE/envs/$CONDA_ENV"

# ── 2. cd to project root ────────────────────────────────────────────────────
cd "$(dirname "$0")"

# ── 3. release DB lock if held ───────────────────────────────────────────────
if command -v lsof &>/dev/null && [ -f "$DB_PATH" ]; then
    LOCK_PIDS=$(lsof "$DB_PATH" 2>/dev/null | awk 'NR>1 {print $2}' | sort -u || true)
    if [ -n "$LOCK_PIDS" ]; then
        log "DuckDB lock held by PID(s): $LOCK_PIDS"
        # only kill ipykernel processes — don't blindly kill unrelated ones
        KERNEL_PIDS=$(ps -p $LOCK_PIDS -o pid=,command= 2>/dev/null \
            | grep ipykernel \
            | awk '{print $1}' || true)
        if [ -n "$KERNEL_PIDS" ]; then
            log "Killing Jupyter kernel(s): $KERNEL_PIDS"
            kill $KERNEL_PIDS 2>/dev/null || true
            sleep 1
        fi
        # re-check for any remaining non-kernel holders
        REMAINING=$(lsof "$DB_PATH" 2>/dev/null | awk 'NR>1 {print $2}' | sort -u || true)
        if [ -n "$REMAINING" ]; then
            err "DB still locked by PID(s): $REMAINING"
            err "These are not Jupyter kernels — kill them manually before retrying."
            exit 1
        fi
    fi
fi

# ── 4. run the pipeline ──────────────────────────────────────────────────────
log "Starting pipeline with env: $CONDA_ENV"
"$PYTHON" "$SCRIPT" "$@"