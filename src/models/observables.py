from pysb import *
from models.monomers import (ACTIVE, INACTIVE, UNPHOSPHORYLATED, 
                           PHOSPHORYLATED, DOUBLY_PHOSPHORYLATED, BOUND)

def declare_observables(model):
    """Define model observables for analysis"""
    
    Observable('Diff_Cells', 
              model.monomers['CellState'](diff_state='diff'))
    
    # Total active AP1 factors
    Observable('AP1_Active',
              model.monomers['cJUN'](state=ACTIVE) +
              model.monomers['JUND'](state=ACTIVE) +
              model.monomers['FRA1'](state=ACTIVE))
    
    # Combined drug effect
    Observable('Drug_Effect',
              model.monomers['Vemurafenib'](bound=BOUND) +
              model.monomers['Trametinib'](bound=BOUND))

    # Add individual observables for plotting
    Observable('ERK_P',
              model.monomers['ERK'](state=PHOSPHORYLATED))
    
    Observable('BRAF_active',
              model.monomers['BRAF'](state=ACTIVE))
    
    Observable('Cell_diff',
              model.monomers['CellState'](diff_state='diff'))

    # Add to existing observables
    Observable('MEK_ERK_Oscillation',
              model.monomers['MEK'](state=DOUBLY_PHOSPHORYLATED) % 
              model.monomers['ERK'](state=DOUBLY_PHOSPHORYLATED))
    
    Observable('RTK_Feedback',
              model.monomers['RTK'](state=ACTIVE))

    # Add after existing observables
    Observable('ERK_Activity_Cycle',
              model.monomers['ERK'](state=DOUBLY_PHOSPHORYLATED)) 