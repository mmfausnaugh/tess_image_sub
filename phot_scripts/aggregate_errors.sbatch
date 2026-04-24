#!/usr/bin/env bash
#SBATCH --job-name="agg_errors"
#SBATCH --output=/lustre/research/mfausnau/logs/%x.o%A
#SBATCH --error=/lustre/research/mfausnau/logs/%x.e%A
#SBATCH --partition=nocona
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=0-0:30:00

set -eo pipefail

logdir="/lustre/research/mfausnau/logs"
dhome=$(pwd)

# Arguments: <sector> <cam> <ccd> <lcdir> <do_phot_jobid1> [...] -- <copy_phot_jobid1> [...]
# For sarchast_submit_all: cam and ccd will be "all"
if [[ $# -lt 5 ]]; then
    echo "Usage: $0 <sector> <cam> <ccd> <lcdir> <do_phot_jobid1> [...] -- <copy_phot_jobid1> [...]"
    exit 1
fi

sector=$1
cam=$2
ccd=$3
lcdir=$4
shift 4

# Split remaining args on "--" into do_phot and copy_phot job ID lists
do_phot_jobids=()
copy_phot_jobids=()
target=do_phot_jobids
for arg in "$@"; do
    if [[ "$arg" == "--" ]]; then
        target=copy_phot_jobids
    else
        eval "${target}+=("\$arg")"
    fi
done

sectoruse=$(printf "s%04d" "$sector")
timestamp=$(date +%Y%m%d_%H%M%S)
outfile="$dhome/errorlog-${sectoruse}-cam${cam}-ccd${ccd}-${timestamp}.txt"

echo "Aggregating errors for sector=$sectoruse cam=$cam ccd=$ccd"
echo "do_phot job IDs:   ${do_phot_jobids[*]}"
echo "copy_phot job IDs: ${copy_phot_jobids[*]}"
echo "Output: $outfile"

{
    echo "========================================================"
    echo " Error report for sector=$sectoruse cam=$cam ccd=$ccd"
    echo " lcdir=$lcdir"
    echo " Generated: $(date)"
    echo " do_phot job IDs:   ${do_phot_jobids[*]}"
    echo " copy_phot job IDs: ${copy_phot_jobids[*]}"
    echo "========================================================"
    echo ""

    total_failed=0

    echo "--- do_phot failures ---"
    echo ""

    for jobid in "${do_phot_jobids[@]}"; do
        # Find all error log files for this job ID
        mapfile -t efiles < <(ls "$logdir/do_phot.e${jobid}_"* 2>/dev/null || true)

        if [[ ${#efiles[@]} -eq 0 ]]; then
            echo "WARNING: No error log files found for job $jobid"
            continue
        fi

        for efile in "${efiles[@]}"; do
            # Extract FAILED lines from this task's log
            mapfile -t failed_lines < <(grep "^(FAILED|WARNING):" "$efile" 2>/dev/null || true)

            if [[ ${#failed_lines[@]} -eq 0 ]]; then
                continue
            fi

            task_id=$(basename "$efile" | grep -oP '(?<=_)\d+$')
            echo "--- Job ${jobid}, task ${task_id} ---"

            for line in "${failed_lines[@]}"; do
                echo "  $line"

                # Extract slice directory path from the FAILED line
                # Format: FAILED: phot2.csh in <path> (exit N)
                slice_path=$(echo "$line" | grep -oP '(?<=in ).*(?= \(exit)')

                # Strip /bkg_phot suffix if present to get the base slice dir
                base_slice="${slice_path%/bkg_phot}"

                # Read the dates file if it exists
                dates_file="$base_slice/dates"
                if [[ -e "$dates_file" ]]; then
                    echo "  Dates:"
                    sed 's/^/    /' "$dates_file"
                else
                    echo "  Dates: (dates file not found in $base_slice)"
                fi
                echo ""
                (( total_failed++ )) || true
            done
        done
    done

    echo "--- copy_phot errors ---"
    echo ""

    # ---- copy_phot errors (content of error logs only, no dates) ----
    copy_errors_found=0
    for jobid in "${copy_phot_jobids[@]}"; do
        mapfile -t efiles < <(ls "$logdir/copy_phot.e${jobid}_"* 2>/dev/null || true)

        if [[ ${#efiles[@]} -eq 0 ]]; then
            echo "WARNING: No error log files found for copy_phot job $jobid"
            continue
        fi

        for efile in "${efiles[@]}"; do
            # Skip empty error logs
            if [[ ! -s "$efile" ]]; then
                continue
            fi
            task_id=$(basename "$efile" | grep -oP '(?<=_)\d+$')
            echo "--- copy_phot job ${jobid}, task ${task_id} ---"
            cat "$efile"
            echo ""
            (( copy_errors_found++ )) || true
        done
    done

    if [[ $copy_errors_found -eq 0 ]]; then
        echo "(No copy_phot errors found)"
        echo ""
    fi

    echo "========================================================"
    echo " Total failed phot2.csh calls: $total_failed"
    echo " copy_phot tasks with errors:  $copy_errors_found"
    echo "========================================================"

} > "$outfile"

echo "Done. $total_failed failure(s) reported."
cat "$outfile"
