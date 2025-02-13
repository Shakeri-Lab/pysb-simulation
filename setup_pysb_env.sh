#!/bin/bash

# Download and install Miniconda if not already installed
if [ ! -d "$HOME/.local/miniconda3" ]; then
    echo "Downloading Miniconda..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    
    echo "Installing Miniconda..."
    bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/.local/miniconda3
    
    # Initialize conda for bash shell
    echo "Initializing conda..."
    source $HOME/.local/miniconda3/bin/activate
    
    # Add conda initialization to .bashrc if not already present
    if ! grep -q "conda initialize" ~/.bashrc; then
        $HOME/.local/miniconda3/bin/conda init bash
    fi
    
    # Clean up
    rm Miniconda3-latest-Linux-x86_64.sh
fi

# Make sure conda is initialized
source $HOME/.local/miniconda3/bin/activate

# Create new environment for PySB
echo "Creating conda environment for PySB..."
conda create -n pysb_env python=3.9 -y

# Activate the environment
echo "Activating environment..."
conda activate pysb_env

# Install all dependencies with version pinning
conda install -y -c conda-forge \
    numpy=1.24.* \
    matplotlib=3.7.* \
    h5py=3.8.* \
    tqdm=4.65.* \
    scipy=1.10.* \
    pandas=2.0.* \
    cython=0.29.* \
    cudatoolkit=11.8.* \
    cupy=11.* \
    numba=0.57.* \
    networkx=3.1.* \
    sympy=1.12.* \
    pytest=7.4.* \
    pytest-cov=4.1.* \
    black=23.7.* \
    flake8=6.1.*

# Install PySB last to avoid dependency conflicts
conda install -y -c alubbock pysb=1.13.*

# Verify CUDA installation
if command -v nvidia-smi &> /dev/null; then
    echo "CUDA installation verified:"
    nvidia-smi
else
    echo "Warning: NVIDIA driver not found. CUDA acceleration may not be available."
fi

# List all installed packages for verification
echo "Installed packages:"
conda list

echo "Setup complete! Use 'conda activate pysb_env' to activate the environment" 