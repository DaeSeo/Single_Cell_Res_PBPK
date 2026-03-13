# Inference/cell_volume.py

"""
Cell Volume Reference Module
Units: um^3 (Cubic Micrometers)
Conversion: 1 um^3 = 1e-15 Liters
"""

VOL_ADIPOSE = 50000       
VOL_GIANT = 25000         
VOL_HEPATOCYTE = 15000    
VOL_LARGE_EPI = 3500      
VOL_STANDARD = 1500       
VOL_SMALL_SUPPORT = 800   
VOL_IMMUNE = 400          
VOL_VASCULAR = 150        

def get_volume_by_name(cell_name):
    name = cell_name.lower()
    if 'adipocyte' in name: return VOL_ADIPOSE
    if 'cardiomyocyte' in name: return VOL_GIANT
    if 'hepatocyte' in name: return VOL_HEPATOCYTE
    if any(x in name for x in ['keratinocyte', 'alveolar cells type 1', 'proximal tubule', 'secretory']):
        return VOL_LARGE_EPI
    if any(x in name for x in ['fibroblast', 'neuron', 'astrocyte', 'alveolar cells type 2', 'podocyte']):
        return VOL_STANDARD
    if any(x in name for x in ['pericyte', 'glia', 'muscle', 'epithelial', 'ciliated', 'stellate']):
        return VOL_SMALL_SUPPORT
    if any(x in name for x in ['cell', 'macrophage', 'monocyte', 'kupffer', 'mast', 'neutrophil', 'cdc', 'pdc', 't-cell', 'b-cell']):
        return VOL_IMMUNE
    if any(x in name for x in ['endothelial', 'erythrocyte', 'platelet']):
        return VOL_VASCULAR
    return 1000

def get_total_volume_L(cell_type, cell_count):
    vol_um3 = get_volume_by_name(cell_type)
    return (vol_um3 * cell_count) * 1e-15