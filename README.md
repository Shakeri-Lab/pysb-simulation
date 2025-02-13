# PYSB Simulation Framework

A framework for simulating MAPK pathway dynamics using PySB.

## Setup

1. Clone this repository: 
```bash
git clone <repository-url>
cd <repository-name>
```

2. Make the setup script executable and run it:

```bash
chmod +x setup_pysb_env.sh
./setup_pysb_env.sh
```

3. Activate the environment:
```bash
source ~/.bashrc
conda activate pysb_env
```

## Model Structure

The model consists of several components (see `src/main_my.py`, startLine: 20, endLine: 39):
- MAPK pathway components
- AP1 transcription factors
- Cell state transitions
- Oscillatory behavior

## Running Simulations

### Single Cell Simulation
For deterministic ODE simulations (see `src/main.py`, startLine: 23, endLine: 170):
```bash
python src/main.py \
    --cell-line mutant \
    --drug-concentration 1.0 0.5 \
    --output results/single_cell.h5 \
    --plot-output results/single_cell.png
```

### Population Simulation
For stochastic simulations (see `src/main_my.py`, startLine: 128, endLine: 162):
```bash
python src/main_my.py \
    --cell-line mutant \
    --drug-concentration 1.0 0.5 \
    --output results/population.h5 \
    --plot-output results/population.png \
    --n-cells-plot 5
```

### Command Line Arguments
- `--cell-line`: Choose between 'mutant' or 'wildtype'
- `--drug-concentration`: Two float values [MEKi, EGF]
- `--output`: Path for HDF5 results file
- `--plot-output`: Path for output plots
- `--n-cells-plot`: Number of cells to plot (population only)
- `--skip-simulation`: Skip simulation if results exist

## Time Points
The simulation uses non-uniform time points (see `src/main.py`, startLine: 111, endLine: 119):
- Early phase: 0-600s, 24 points
- Middle phase: 600-3600s, 10 points
- Late phase: 3600-7200s, 5 points
- Pre-equilibration: -600-0s, 4 points

## Output Files

### Data Files
HDF5 files containing:
- Time series data
- Species trajectories
- Metadata (cell line, drug concentrations)

### Plots
Two visualization options:

1. Basic Plotting (see `src/plot_results.py`, startLine: 10, endLine: 58):
- ERK Phosphorylation
- MEK Phosphorylation
- RAS Activity

2. Advanced Visualization (see `src/visualization.py`, startLine: 22, endLine: 52):
- Individual cell trajectories
- Population means
- Standard deviations
- Custom observable plotting

## Model Parameters
Cell line-specific parameters (see `src/models/old/parameters.py`, startLine: 1, endLine: 23):
- Mutant cells: Higher baseline differentiation, stronger ERK dependence
- Wildtype cells: More epigenetic plasticity, slower differentiation

## Dependencies
All required packages are installed via `setup_pysb_env.sh`:
- Core: numpy, scipy, pandas
- Visualization: matplotlib, seaborn
- Computation: cython, numba
- GPU Support: cudatoolkit, cupy
- Development: pytest, black, flake8

## Citation
If you use this code in your research, please cite:
[Citation information to be added]

## SLURM Submission

Submit jobs using the provided SLURM script:
```bash
sbatch run_simulation.slurm
```

SLURM configuration:
- Partition: standard
- Memory: 16GB
- CPUs: 8
- Time limit: 12 hours

## Visualization

Additional plotting tools are available (see `src/visualization.py`, startLine: 1, endLine: 53):
```bash
python src/plot_results.py \
    --results-file results/simulation_results.h5 \
    --n-cells 5
```

## Post-Processing Analysis

For detailed analysis of simulation results, use the post-processing script:
```bash
python src/postprocess.py --input results/simulation_results.h5
```

This will:
- Generate detailed plots of species trajectories
- Save plots to `results/analysis/species_trajectories.png`
- Print statistics about the simulation data
- Show time evolution of first 8 species
- Display min/max concentrations for each species

The script provides:
- Time series visualization
- Basic statistical analysis
- Concentration ranges for each species
- Metadata from simulation conditions

Output location:
- Plots: `results/analysis/species_trajectories.png`
- Logging: Terminal output with statistics and file paths

## Troubleshooting

1. Cython compilation errors:
```bash
conda activate pysb_env
conda install cython
```

2. Missing dependencies:
```bash
conda install -c conda-forge <package_name>
```

3. CUDA Limitations:
Our model contains complex expressions and rules (see `src/main.py`, startLine: 74, endLine: 86) that are not compatible with CUDA-based solvers. Therefore, we use the CPU-based ODE solver (ScipyOdeSimulator) with Cython compilation for optimal performance. If you encounter CUDA-related errors:
- Use `simulator_type='ode'` instead of 'sde'
- Ensure Cython is properly installed
- The simulation will automatically use CPU-based computation

Note: While CUDA-based solvers can offer significant speedup for certain types of models, they are limited to simpler reaction networks without complex expressions. Our model's sophistication requires the more flexible CPU-based solver.

3. Initialize and push to GitHub:

```bash
# Initialize git repository
git init

# Add files
git add .gitignore README.md setup_pysb_env.sh src/ run_pysb.slurm

# Initial commit
git commit -m "Initial commit: PYSB simulation framework"

# Create new repository on GitHub through web interface
# Then link and push:
git remote add origin https://github.com/YOUR_USERNAME/pysb-simulation.git
git branch -M main
git push -u origin main
```

The code structure we're pushing is based on:
- Main simulation code (startLine: 1, endLine: 181 in `src/main.py`)
- Parameter handling (startLine: 1, endLine: 23 in `src/models/old/parameters.py`)
- Plotting utilities (startLine: 1, endLine: 58 in `src/plot_results.py`)

Would you like me to help with creating the GitHub repository through the GitHub API, or would you prefer to create it manually through the web interface?
