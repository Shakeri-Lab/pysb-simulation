import h5py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def plot_cell_trajectories(results_file, n_cells_to_plot=1):
    """Plot trajectories from simulation results."""
    with h5py.File(results_file, 'r') as f:
        time = f['time'][:].flatten()  # Ensure 1D array
        trajectories = f['trajectories'][:]
        # Try to get metadata if it exists
        cell_type = f.attrs.get('cell_line', 'unknown')
        meki_conc = f.attrs.get('meki_concentration', 0)
        egf_conc = f.attrs.get('egf_concentration', 0)
    
    # Create results directory if it doesn't exist
    results_dir = Path('results')
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Create figure with subplots
    fig = plt.figure(figsize=(15, 10))
    gs = GridSpec(2, 2, figure=fig)
    
    # Plot with condition information in title
    title = f"{cell_type.upper()} cells\nMEKi: {meki_conc:.1f}, EGF: {egf_conc:.1f}"
    fig.suptitle(title, fontsize=12)
    
    # Create subplots
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])
    
    # Plot key species (ensure 1D arrays)
    ax1.plot(time, trajectories[:, 16], alpha=0.7, label='pERK')
    ax2.plot(time, trajectories[:, 14], alpha=0.7, label='pMEK')
    ax3.plot(time, trajectories[:, 8], alpha=0.7, label='gtpRAS')
    
    # Customize plots
    ax1.set_title('ERK Phosphorylation')
    ax1.set_xlabel('Time (min)')  # Changed to minutes
    ax1.set_ylabel('Concentration')
    ax1.legend()
    
    ax2.set_title('MEK Phosphorylation')
    ax2.set_xlabel('Time (min)')  # Changed to minutes
    ax2.set_ylabel('Concentration')
    ax2.legend()
    
    ax3.set_title('RAS Activity')
    ax3.set_xlabel('Time (min)')  # Changed to minutes
    ax3.set_ylabel('Concentration')
    ax3.legend()
    
    plt.tight_layout()
    plot_path = results_dir / 'trajectories.png'
    plt.savefig(plot_path, dpi=300)
    plt.close()
    logger.info(f"Plot saved to {plot_path}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results-file', type=str, 
                       default='/project/shakeri-lab/AP_1/pysb/results/cell_simulation_results.h5')
    parser.add_argument('--n-cells', type=int, default=5)
    args = parser.parse_args()
    
    plot_cell_trajectories(args.results_file, args.n_cells) 