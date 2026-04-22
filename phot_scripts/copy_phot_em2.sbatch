#!/usr/bin/env bash
#SBATCH --job-name="copy_phot"
#SBATCH --output=/lustre/research/mfausnau/logs/%x.o%A_%a
#SBATCH --error=/lustre/research/mfausnau/logs/%x.e%A_%a
#SBATCH --partition=nocona
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
#SBATCH --array=0-99%50
#SBATCH --time=0-1:30:00

set -eo pipefail

# Number of array tasks — used as modulo to distribute slices
n_tasks=$(( SLURM_ARRAY_TASK_MAX + 1 ))

duse=$DATA_DIR
dhome=$(pwd)
sector=$1
sectoruse=$(printf "s%04d" "$1")
cam=$2
ccd=$3
o=$4
lcdir=$5

echo "sector use: $sectoruse  cam: $cam  ccd: $ccd  orbit: $o  lcdir: $lcdir"

mapfile -t folders < <(ls -d "$duse/$sectoruse/cam${cam}-ccd${ccd}/$o/slice"*)
nelements=${#folders[@]}

if [[ $nelements -eq 0 ]]; then
    echo "ERROR: No slice directories found."
    exit 1
fi

# --- One-time output directory setup: task 1, first slice only ---
if [[ $SLURM_ARRAY_TASK_ID -eq 1 ]]; then
    outbase="$dhome/sector${sector}/cam${cam}_ccd${ccd}"
    mkdir -p "$outbase/$lcdir"
    mkdir -p "$outbase/bkg_phot"
    mkdir -p "$outbase/bkg_phot/$lcdir"
fi

for (( ii=1; ii<=nelements; ii++ )); do
    if [[ $(( ii % n_tasks )) -ne $SLURM_ARRAY_TASK_ID ]]; then
        continue
    fi

    slice_dir="${folders[$((ii-1))]}"
    cd "$slice_dir/$lcdir"
    echo "Copying lc files from: $(pwd)"

    if compgen -G "lc_*" > /dev/null; then
        for f in lc_*; do
            cat "$f" >> "$dhome/sector${sector}/cam${cam}_ccd${ccd}/$lcdir/$f"
        done
    else
        echo "WARNING: No lc_* files found in $(pwd)"
    fi

    cd "../bkg_phot/$lcdir"
    echo "Copying bkg lc files from: $(pwd)"

    if compgen -G "lc_*" > /dev/null; then
        for f in lc_*; do
            cat "$f" >> "$dhome/sector${sector}/cam${cam}_ccd${ccd}/bkg_phot/$lcdir/$f"
        done
    else
        echo "WARNING: No lc_* files found in $(pwd)"
    fi

    cd "$dhome"
done
