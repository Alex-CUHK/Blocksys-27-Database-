"""Sync regenerated experiment inputs and rebuild final manuscript layout figures."""
from pathlib import Path
import shutil,subprocess,sys
root=Path(__file__).resolve().parents[1]
out=root/'experiment/outputs/workload_weighted';fig=root/'manuscript/figures'
for src,dst in [('weighted_matrices.json','weighted_matrix_inputs.json'),('sensitivity_results.csv','weighted_sensitivity_results.csv'),('figure2_matrices.pdf','weighted_matrices.pdf'),('figure2_matrices.png','weighted_matrices.png')]:
 shutil.copy2(out/src,fig/dst)
for name in ['plot_weighted_layout.py','plot_weighted_combined.py','plot_eight_panels.py']:
 subprocess.run([sys.executable,str(root/'manuscript/scripts'/name)],check=True)
