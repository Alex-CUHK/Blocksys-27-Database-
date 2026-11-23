"""Combine the original plotting code as a vector 2-row by 4-column figure."""
from pathlib import Path
import runpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
original_subplots=plt.subplots
original_savefig=matplotlib.figure.Figure.savefig
original_close=plt.close
fig,axes=original_subplots(2,4,figsize=(16,7.5),layout='constrained')
row=0
def subplots(*args,**kwargs):
 return fig,np.asarray(axes[row]).reshape(2,2)
plt.subplots=subplots
matplotlib.figure.Figure.savefig=lambda *args,**kwargs:None
plt.close=lambda *args,**kwargs:None
for row,script in enumerate(['plot_layout_cost.py','plot_weighted_layout.py']):
 runpy.run_path(str(ROOT/'scripts'/script),run_name='__main__')
plt.subplots=original_subplots
matplotlib.figure.Figure.savefig=original_savefig
plt.close=original_close
for k,ax in enumerate(axes.flat):
 title=ax.get_title()
 if title.startswith('('):title=title[4:]
 ax.set_title(f'({chr(97+k)}) {title}',fontsize=10)
 ax.tick_params(labelsize=8)
 ax.xaxis.label.set_size(9)
 ax.yaxis.label.set_size(9)
fig.get_layout_engine().set(hspace=.15,wspace=.04)
for ext in ['pdf','png']:fig.savefig(ROOT/f'figures/layout_eight_panels.{ext}',dpi=180,bbox_inches='tight')
