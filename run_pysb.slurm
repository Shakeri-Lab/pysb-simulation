#!/bin/bash
#SBATCH --job-name=pysb_sim
#SBATCH --output=pysb_sim_%j.out
#SBATCH --error=pysb_sim_%j.err
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH -A shakeri-lab
#SBATCH --mem=64G
#SBATCH --cpus-per-task=1

# Print job information
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "Start time: $(date)"

# Load only CUDA
module load cuda/12.4.1

# Initialize conda
eval "$(/home/$USER/.local/miniconda3/bin/conda shell.bash hook)"
conda activate pysb_env

# Verify environment and packages
echo "Python: $(which python)"
echo "Conda env: $CONDA_DEFAULT_ENV"
pip list | grep tqdm

# Set CUDA environment variables
export CUDA_VISIBLE_DEVICES=$SLURM_LOCALID
export PYSB_LOG=INFO

# Print environment information
echo "Python version:"
python --version
echo "CUDA devices:"
echo $CUDA_VISIBLE_DEVICES
echo "GPU information:"
nvidia-smi

# Try importing pysb directly
echo "Testing PySB import..."
python -c "import pysb; print(f'PySB version: {pysb.__version__}')"

# Run multiple simulations with different conditions
echo "Starting simulations..."

# # Wildtype cells without drugs
# python -u src/main.py \
#     --cell-line wildtype \
#     --drug-concentration 0.0 0.0 \
#     --output results/wildtype_control.h5 \
#     --plot-output results/wildtype_control.png

# # Wildtype cells with MEKi
# python -u src/main.py \
#     --cell-line wildtype \
#     --drug-concentration 1.0 0.0 \
#     --output results/wildtype_meki.h5 \
#     --plot-output results/wildtype_meki.png

# Mutant cells without drugs
python -u src/main.py \
    --cell-line mutant \
    --drug-concentration 0.0 0.0 \
    --output results/mutant_control.h5 \
    --plot-output results/mutant_control.png

# # Mutant cells with MEKi
# python -u src/main.py \
#     --cell-line mutant \
#     --drug-concentration 1.0 0.0 \
#     --output results/mutant_meki.h5 \
#     --plot-output results/mutant_meki.png

# # Mutant cells with MEKi and EGF stimulation
# python -u src/main.py \
#     --cell-line mutant \
#     --drug-concentration 1.0 0.5 \
#     --output results/mutant_meki_egf.h5 \
#     --plot-output results/mutant_meki_egf.png

echo "End time: $(date)"