import h5py
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_trajectories(h5_file):
    """Analyze and plot species trajectories from HDF5 file."""
    logger.info(f"Reading data from {h5_file}")
    
    try:
        with h5py.File(h5_file, 'r') as f:
            # Load data
            time = f['time'][:].flatten()  # Ensure 1D array
            trajectories = f['trajectories'][:]
            
            # Get metadata
            cell_type = f.attrs.get('cell_line', 'unknown')
            meki_conc = f.attrs.get('meki_concentration', 0)
            egf_conc = f.attrs.get('egf_concentration', 0)
            
            # Print basic statistics
            logger.info("\nData Statistics:")
            logger.info("--------------")
            logger.info(f"Time points: {len(time)}")
            logger.info(f"Number of species: {trajectories.shape[1]}")
            logger.info(f"Time range: [{time.min():.1f}, {time.max():.1f}]")
            
            # Create figure
            fig, axes = plt.subplots(4, 2, figsize=(15, 20))
            fig.suptitle(f"{cell_type.upper()} cells\nMEKi: {meki_conc:.1f}, EGF: {egf_conc:.1f}")
            
            # Plot all species
            for i in range(min(8, trajectories.shape[1])):
                ax = axes[i//2, i%2]
                ax.plot(time, trajectories[:, i], 'b-', label=f'Species {i}')
                ax.set_xlabel('Time (min)')
                ax.set_ylabel('Concentration')
                ax.set_title(f'Species {i}')
                ax.grid(True)
                
                # Add min/max annotations
                ymin, ymax = trajectories[:, i].min(), trajectories[:, i].max()
                ax.annotate(f'Min: {ymin:.2e}', xy=(0.02, 0.02), xycoords='axes fraction')
                ax.annotate(f'Max: {ymax:.2e}', xy=(0.02, 0.95), xycoords='axes fraction')
            
            plt.tight_layout()
            
            # Save plot
            output_dir = Path('results/analysis')
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / 'species_trajectories.png'
            logger.info(f"Saving plot to {output_path}")
            plt.savefig(output_path)
            plt.close()
            
    except FileNotFoundError:
        logger.error(f"Could not find file: {h5_file}")
    except Exception as e:
        logger.error(f"Error processing file: {e}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True,
                       help='Path to HDF5 results file')
    args = parser.parse_args()
    
    analyze_trajectories(args.input) 