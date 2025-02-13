from pysb.simulator import ScipyOdeSimulator
import matplotlib.pyplot as plt
from models.RTKERK__pRAF import model
from parameters import load_parameters
from paths import get_parameters_file
import argparse
import numpy as np
from pathlib import Path
import pysb.bng
import os
from pysb import Parameter
from pysb.export import export
import time
import logging
import h5py
import pickle  # Add this import at the top
from plot_results import plot_cell_trajectories

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_simulation(args):
    start_time = time.time()
    logger.info("Starting simulation setup...")
    
    # Check if results exist and handle skip option
    if args.skip_simulation and os.path.exists(args.output):
        logger.info(f"Loading existing results from {args.output}")
        plot_cell_trajectories(args.output)
        return
        
    # Set up output directory
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    # Define settings dictionary
    settings = {
        'model_name': 'RTKERK',
        'variant': 'pRAF' if args.cell_line == 'mutant' else 'base',
        'dataset': 'EGF_EGFR_MEKi_PRAFi_RAFi'
    }
    
    # Ensure parameters directory exists
    param_file = get_parameters_file(settings['model_name'], 
                                   settings['variant'], 
                                   settings['dataset'])
    os.makedirs(os.path.dirname(param_file), exist_ok=True)
    
    # Set minimum concentration to avoid log(0)
    MIN_CONC = 1e-6
    
    # Add BRAF_mut_0 parameter if it doesn't exist
    try:
        model.parameters['BRAF_mut_0']
    except KeyError:
        print("Adding BRAF_mut_0 parameter to model")
        model.add_component(Parameter('BRAF_mut_0', MIN_CONC))
    
    # Initialize all parameters with minimum values first
    for param in model.parameters.values():
        if param.value == 0:
            param.value = MIN_CONC
    
    # Set BRAF mutation status based on cell line
    model.parameters['BRAF_mut_0'].value = 100 if args.cell_line == 'mutant' else MIN_CONC
    
    # Load parameters for specific drug combination
    try:
        parameters = load_parameters(
            model,
            settings,
            prafi=None,
            rafi='Vemurafenib' if args.drug_concentration[0] > MIN_CONC else None,
            meki='Cobimetinib' if args.drug_concentration[1] > MIN_CONC else None,
            allow_missing_pars=True
        )
        
        # Set drug concentrations after parameter loading
        model.parameters['MEKi_0'].value = max(args.drug_concentration[0], MIN_CONC)
        model.parameters['EGF_0'].value = max(args.drug_concentration[1], MIN_CONC)
        
        # Double check all parameters are non-zero
        for param in model.parameters.values():
            if param.value <= 0:
                param.value = MIN_CONC
                print(f"Warning: Parameter {param.name} was <= 0, set to {MIN_CONC}")
        
    except Exception as e:
        print(f"Warning: Could not load parameters from {param_file}: {e}")
        print("Using default parameters from model definition")
    
    # Cache equations
    cache_file = f"cached_equations_{args.cell_line}.pkl"
    if os.path.exists(cache_file):
        logger.info("Loading cached equations...")
        # Generate equations first
        pysb.bng.generate_equations(model, cleanup=False)
        # Then verify against cache
        with open(cache_file, 'rb') as f:
            cached_odes = pickle.load(f)
            if not np.array_equal(model.odes, cached_odes):
                logger.warning("Cached equations don't match, regenerating...")
                pysb.bng.generate_equations(model, cleanup=False)
    else:
        logger.info("Generating equations...")
        pysb.bng.generate_equations(model, cleanup=False)
        with open(cache_file, 'wb') as f:
            pickle.dump(model.odes, f)
    
    # Configure simulator with optimized settings for single cell
    # Create non-uniform time points with higher resolution at the beginning
    early_times = np.linspace(0, 600, 30)      # First 10 min, 2-min intervals
    mid_times = np.linspace(600, 3600, 20)     # Next 50 min, ~16-min intervals
    late_times = np.linspace(3600, 7200, 10)   # Last 60 min, 60-min intervals

    # Add pre-equilibration period
    equil_time = np.linspace(-600, 0, 4)      # 10 minutes pre-equilibration, ~3-min intervals
    stim_time = np.concatenate([early_times, mid_times, late_times])
    tspan = np.unique(np.concatenate([equil_time, stim_time]))

    # Set initial EGF to zero, then add it at t=0
    initial_egf = model.parameters['EGF_0'].value
    model.parameters['EGF_0'].value = MIN_CONC

    sim = ScipyOdeSimulator(
        model,
        tspan=tspan,
        compiler='cython',
        integrator='lsoda',
        integrator_options={
            'rtol': 1e-6,  # Tighter tolerance
            'atol': 1e-8,
            'mxstep': 10000,  # Increased max steps for stiff equations
        }
    )

    # Run pre-equilibration
    equil_output = sim.run(tspan=equil_time)

    # Set EGF stimulus and continue simulation
    model.parameters['EGF_0'].value = initial_egf

    # Run simulation with detailed timing
    logger.info("Starting numerical integration...")
    setup_time = (time.time() - start_time) / 60
    logger.info(f"Setup took {setup_time:.2f} minutes")

    integration_start = time.time()
    output = sim.run()
    integration_time = (time.time() - integration_start) / 60
    logger.info(f"Integration took {integration_time:.2f} minutes")

    # Debug output shows:
    logger.info(f"Number of time points: {len(output.tout)}")
    logger.info(f"Time points: {output.tout}")
    logger.info(f"Shape of species trajectories: {output.species.shape}")

    # Save results with metadata
    save_start = time.time()
    with h5py.File(args.output, 'w') as f:
        f.create_dataset('time', data=output.tout)
        f.create_dataset('trajectories', data=output.species)
        # Add metadata
        f.attrs['cell_line'] = args.cell_line
        f.attrs['meki_concentration'] = args.drug_concentration[0]
        f.attrs['egf_concentration'] = args.drug_concentration[1]
    save_time = (time.time() - save_start) / 60
    logger.info(f"Saving results took {save_time:.2f} minutes")
    
    # Plot results
    plot_cell_trajectories(args.output)
    
    total_time = (time.time() - start_time) / 60
    logger.info(f"Total simulation pipeline took {total_time:.2f} minutes")

    def check_hdf5_content(filename):
        with h5py.File(filename, 'r') as f:
            print("\nHDF5 File Content:")
            print("------------------")
            print("Datasets:", list(f.keys()))
            print("Time shape:", f['time'][:].shape)
            print("Time points:", f['time'][:])
            print("Trajectories shape:", f['trajectories'][:].shape)
            print("First few trajectory values:", f['trajectories'][0,:10])
            print("\nMetadata:")
            print("------------------")
            for key in f.attrs:
                print(f"{key}: {f.attrs[key]}")

    check_hdf5_content(args.output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cell-line', choices=['wildtype', 'mutant'], required=True)
    parser.add_argument('--drug-concentration', nargs=2, type=float, required=True)
    parser.add_argument('--output', type=str, default='results/simulation_results.h5')
    parser.add_argument('--plot-output', type=str, default='results/trajectories.png')
    parser.add_argument('--skip-simulation', action='store_true',
                       help='Skip simulation if results exist')
    args = parser.parse_args()
    
    run_simulation(args) 