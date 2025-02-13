from pysb import *
from models.monomers import declare_monomers
from models.mapk import declare_mapk_rules
from models.ap1 import declare_ap1_rules
from models.cell_state import declare_cell_state_rules
from models.old.simulation import ModelSimulator
from models.old.parameters import declare_cell_line_parameters
from models.observables import declare_observables
from models.validation import validate_states
from models.oscillations import declare_oscillation_rules
import os
import h5py
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
from models.monomers import (UNPHOSPHORYLATED, PHOSPHORYLATED, 
                             DOUBLY_PHOSPHORYLATED, INACTIVE, ACTIVE, 
                             MUTANT, UNBOUND, BOUND)

def build_model():
    """Construct the complete model"""
    model = Model()
    
    # Declare model components
    declare_monomers(model)
    
    # Add observables first
    declare_observables(model)
    
    # Then declare rules
    declare_mapk_rules(model)
    declare_ap1_rules(model)
    declare_cell_state_rules(model)
    declare_oscillation_rules(model)
    
    # Validate state definitions
    validate_states(model)
    
    return model

def plot_cell_trajectories(output_file, cell_indices=[0,1,2]):
    """Plot observables for selected cells from simulation results"""
    with h5py.File(output_file, 'r') as f:
        time = f['time'][:]
        trajectories = f['trajectories'][:]
    
    # Get observable names from the model definition
    observables = [
        'ERK_P', 
        'BRAF_active',
        'AP1_Active',
        'Diff_Cells',
        'Drug_Effect',
        'ERK_Activity_Cycle'
    ]
    
    fig = plt.figure(figsize=(12, 8))
    gs = GridSpec(3, 2, figure=fig)
    axs = [fig.add_subplot(gs[i,j]) for i in range(3) for j in range(2)]
    
    for idx in cell_indices:
        cell_data = trajectories[idx]
        
        for i, obs in enumerate(observables):
            ax = axs[i]
            ax.plot(time, cell_data[:,i], 
                   label=f'Cell {idx}' if i==0 else None,
                   alpha=0.7)
            ax.set_ylabel(obs)
            ax.set_xlabel('Time')
            if obs in ['AP1_Active', 'ERK_Activity_Cycle']:
                ax.set_yscale('log')
    
    axs[0].legend()
    plt.tight_layout()
    plt.savefig('cell_trajectories.png')
    plt.close()

def plot_population_statistics(results_file, output_plot):
    """Plot population average and confidence intervals for all observables."""
    with h5py.File(results_file, 'r') as f:
        time = f['time'][:]
        trajectories = f['trajectories'][:]
    
    # Define all observables to plot
    observable_names = [
        'ERK_P', 'BRAF_active', 'Cell_diff',
        'Diff_Cells', 'AP1_Active', 'Drug_Effect'
    ]
    
    # Create subplot grid
    n_obs = len(observable_names)
    n_rows = (n_obs + 1) // 2  # 2 columns
    fig, axes = plt.subplots(n_rows, 2, figsize=(15, 4*n_rows))
    axes = axes.flatten()
    
    # Calculate statistics
    mean = np.mean(trajectories, axis=0)
    std = np.std(trajectories, axis=0)
    ci_lower = mean - 1.96 * std / np.sqrt(trajectories.shape[0])
    ci_upper = mean + 1.96 * std / np.sqrt(trajectories.shape[0])
    
    # Plot each observable
    for i, (name, ax) in enumerate(zip(observable_names, axes)):
        # Plot mean
        ax.plot(time, mean[:, i], 'b-', label='Population Mean')
        
        # Plot confidence interval
        ax.fill_between(time, ci_lower[:, i], ci_upper[:, i], 
                       color='b', alpha=0.2, label='95% CI')
        
        ax.set_title(name)
        ax.set_xlabel('Time')
        ax.set_ylabel('Level')
        ax.legend()
    
    # Remove any empty subplots
    for j in range(i+1, len(axes)):
        fig.delaxes(axes[j])
    
    plt.tight_layout()
    base_name = os.path.splitext(output_plot)[0]
    stats_plot = f"{base_name}_all_observables.png"
    plt.savefig(stats_plot)
    plt.close()
    print(f"All observables statistics plot saved to {stats_plot}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--cell-line', choices=['mutant', 'wildtype'], 
                       required=True)
    parser.add_argument('--drug-concentration', type=float, nargs=2)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--plot-output', type=str, 
                       default='results/cell_trajectories.png')
    parser.add_argument('--n-cells-plot', type=int, default=5)
    parser.add_argument('--skip-simulation', action='store_true',
                       help='Skip simulation if results exist')
    args = parser.parse_args()
    
    # Check if simulation results exist
    if args.skip_simulation and os.path.exists(args.output):
        print(f"Loading existing results from {args.output}")
    else:
        print("No existing results found, running simulation...")
        
        # Build and simulate model
        model = build_model()
        simulator = ModelSimulator(model, args.output, simulator_type='sde')
        
        params = {
            'BRAF_mut_0': 100 if args.cell_line == 'mutant' else 0,
            'Vemurafenib_0': args.drug_concentration[0],
            'Trametinib_0': args.drug_concentration[1]
        }
        
        simulator.run_parallel_sims(params)
    
    # Plot results
    plot_cell_trajectories(args.output, args.n_cells_plot)
    plot_population_statistics(args.output, args.plot_output) 