"""
Cell Volume Reference Module (Literature-based / BioNumbers)
Units: um^3 (Cubic Micrometers)
Conversion: 1 um^3 = 1e-15 Liters
"""

# ---------------------------------------------------------
# Literature-based Cell Volumes (um^3)
# ---------------------------------------------------------
VOL_ADIPOCYTE      = 200000    # Massive lipid storage
VOL_CARDIOMYOCYTE  = 20000     # Muscle cells
VOL_HEPATOCYTE     = 10000     # Liver parenchymal cells
VOL_FIBROBLAST     = 4000      # Stromal / Connective tissue (Matched to prior validation)
VOL_EPITHELIAL     = 2000      # Large epithelial, tubular, and secretory cells
VOL_LARGE_IMMUNE   = 1500      # Macrophages, Kupffer cells, DCs
VOL_ENDOTHELIAL    = 800       # Vascular lining
VOL_MID_IMMUNE     = 350       # Neutrophils, Monocytes, Eosinophils
VOL_LYMPHOCYTE     = 200       # T-cells, B-cells, NK-cells
VOL_ERYTHROCYTE    = 90        # Red blood cells
VOL_PLATELET       = 10        # Megakaryocyte fragments
VOL_DEFAULT        = 1000      # Generic fallback

def get_volume_by_name(cell_name):
    name = cell_name.lower()
    
    # 1. Giant & Specialized Cells
    if 'adipocyte' in name or 'fat' in name: return VOL_ADIPOCYTE
    if 'cardiomyocyte' in name: return VOL_CARDIOMYOCYTE
    if 'hepatocyte' in name: return VOL_HEPATOCYTE
    
    # 2. Stromal & Connective Tissue
    if any(x in name for x in ['fibroblast', 'stellate', 'stromal', 'mesenchymal']):
        return VOL_FIBROBLAST
        
    # 3. Epithelial & Secretory
    if any(x in name for x in ['epithelial', 'keratinocyte', 'secretory', 'proximal tubule', 'alveolar', 'podocyte', 'ciliated']):
        return VOL_EPITHELIAL
        
    # 4. Endothelial & Nervous System Support
    if any(x in name for x in ['endothelial', 'pericyte', 'astrocyte', 'glia']):
        return VOL_ENDOTHELIAL
        
    # 5. Large Immune / Phagocytes
    if any(x in name for x in ['macrophage', 'kupffer', 'dendritic', 'cdc', 'pdc', 'mast']):
        return VOL_LARGE_IMMUNE
        
    # 6. Medium Immune (Granulocytes / Monocytes)
    if any(x in name for x in ['neutrophil', 'monocyte', 'eosinophil', 'basophil']):
        return VOL_MID_IMMUNE
        
    # 7. Small Immune (Lymphocytes)
    if any(x in name for x in ['t-cell', 't cell', 'b-cell', 'b cell', 'nk', 'lymphocyte']):
        return VOL_LYMPHOCYTE
        
    # 8. Blood Components (Non-immune)
    if 'erythrocyte' in name or 'red blood' in name: return VOL_ERYTHROCYTE
    if 'platelet' in name: return VOL_PLATELET
    
    # Fallback
    return VOL_DEFAULT

def get_total_volume_L(cell_type, cell_count):
    vol_um3 = get_volume_by_name(cell_type)
    return (vol_um3 * cell_count) * 1e-15