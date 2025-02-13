import h5py
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Define project directories
PROJECT_DIR = Path('/project/shakeri-lab/AP_1/pysb')
RESULTS_DIR = PROJECT_DIR / 'results'

class ResultsVisualizer:
    def __init__(self, results_file):
        """Initialize visualizer with path to HDF5 results file"""
        self.results_file = RESULTS_DIR / results_file
        with h5py.File(self.results_file, 'r') as f:
            self.time = f['time'][:]
            self.trajectories = f['trajectories'][:]
        
        # Ensure results directory exists
        RESULTS_DIR.mkdir(exist_ok=True)

    def plot_time_courses(self, observables=['ERK_pp', 'cJUN_active'], 
                         show_individual=True):
        """Plot time courses with individual trajectories and mean"""
        fig, axes = plt.subplots(len(observables), 1, figsize=(10, 4*len(observables)))
        if len(observables) == 1:
            axes = [axes]

        for ax, observable in zip(axes, observables):
            if show_individual:
                for traj in self.trajectories:
                    ax.plot(self.time, traj[observable], 
                          alpha=0.1, color='gray')

            mean_traj = np.mean(self.trajectories[observable], axis=0)
            std_traj = np.std(self.trajectories[observable], axis=0)
            
            ax.plot(self.time, mean_traj, 'b-', label='Mean')
            ax.fill_between(self.time, 
                          mean_traj - std_traj, 
                          mean_traj + std_traj, 
                          alpha=0.2)
            
            ax.set_xlabel('Time')
            ax.set_ylabel(observable)
            ax.legend()
            ax.grid(True)

        plt.tight_layout()
        save_path = RESULTS_DIR / f'time_courses.png'
        plt.savefig(save_path)
        print(f"Saved time courses plot to: {save_path}")
        plt.close()

    def create_summary_plot(self):
        """Create comprehensive summary plot"""
        fig = plt.figure(figsize=(15, 10))
        
        # 1. Time courses
        ax1 = plt.subplot(221)
        mean_erk = np.mean(self.trajectories['ERK_pp'], axis=0)
        ax1.plot(self.time, mean_erk, 'b-', label='ERK-pp')
        ax1.set_title('ERK Activity')
        ax1.legend()
        
        # 2. AP-1 Balance
        ax2 = plt.subplot(222)
        mean_cjun = np.mean(self.trajectories['cJUN_active'], axis=0)
        mean_fra1 = np.mean(self.trajectories['FRA1_active'], axis=0)
        ax2.plot(self.time, mean_cjun, 'r-', label='cJUN')
        ax2.plot(self.time, mean_fra1, 'g-', label='FRA1')
        ax2.set_title('AP-1 Factor Balance')
        ax2.legend()
        
        plt.tight_layout()
        
        save_path = RESULTS_DIR / 'summary_plot.png'
        plt.savefig(save_path)
        print(f"Saved summary plot to: {save_path}")
        plt.close() 