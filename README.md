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
```bash
python src/main.py \
    --cell-line mutant \
    --drug-concentration 1.0 0.5 \
    --output results/single_cell.h5 \
    --plot-output results/single_cell.png
```

### Population Simulation
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
- `--drug-concentration`: Two float values for drug concentrations
- `--output`: Path for HDF5 results file
- `--plot-output`: Path for output plots
- `--n-cells-plot`: Number of cells to plot (population only)
- `--skip-simulation`: Skip simulation if results exist

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

## Output Files

### Data Files
- HDF5 files containing simulation trajectories
- Time series data for all observables
- Population statistics (for multi-cell simulations)

### Plots
- Single cell trajectories
- Population averages with confidence intervals
- Observable-specific plots including:
  - ERK phosphorylation
  - BRAF activity
  - Cell differentiation state
  - Drug effects

## Visualization

Additional plotting tools are available (see `src/visualization.py`, startLine: 1, endLine: 53):
```bash
python src/plot_results.py \
    --results-file results/simulation_results.h5 \
    --n-cells 5
```

## Model Parameters

Cell line-specific parameters are defined in `src/models/old/parameters.py` (startLine: 1, endLine: 23):
- Mutant: Enhanced ERK dependence and baseline differentiation
- Wildtype: Higher epigenetic plasticity and slower differentiation

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

## Citation

If you use this code in your research, please cite:
[Citation information to be added]
