"""Conceptual workflow, not a measured hardware implementation."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/blocksys-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from pathlib import Path
fig,ax=plt.subplots(figsize=(8,5),layout='constrained');ax.set_xlim(0,10);ax.set_ylim(0,6);ax.axis('off')
def box(x,y,w,h,text,planned=False):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.08',facecolor='#fff4e5' if planned else '#eaf3f8',edgecolor='#9c651a' if planned else '#24546b',linestyle='--' if planned else '-',linewidth=1.2));ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=10)
def arrow(a,b):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=13,color='#555555'))
box(.2,4.6,2.6,1,'Observed block data\n72 probability dates\nper network')
box(3.6,4.6,2.8,1,'Statistical analysis\nStratified mean (Eq. 1)\nSeparate data branch')
arrow((2.9,5.1),(3.5,5.1))
box(.2,2.5,2.6,1.2,'Replay and execution trace\nHistorical state needed',True)
arrow((1.5,4.5),(1.5,3.8))
box(3.6,2.5,2.8,1.2,'Architecture mapping\nTimed communication events\nTraffic T (Eq. 3)',True)
arrow((2.9,3.1),(3.5,3.1))
box(7.2,4.6,2.6,1,'Eight-module abstraction\nStatic connectivity A\n(Eq. 2)')
box(7.2,2.5,2.6,1.2,'Choose weights W\nCurrent pilot: W = A\nFuture trace model: W = T')
arrow((8.5,4.5),(8.5,3.8));arrow((6.5,3.1),(7.1,3.1))
box(3.6,.35,6.2,1.2,'Fixed-slot layout search\nCost C(P,r) (Eq. 4) and optimum P* (Eq. 5)\nPlanar versus two-layer layouts, 8! placements per grid')
arrow((8.5,2.4),(8.5,1.65))
ax.text(.2,.7,'Solid: available model/data\nDashed: pending real-trace stage',fontsize=9,va='center')
out=Path(__file__).resolve().parents[1]/'figures';fig.savefig(out/'model_workflow.pdf',bbox_inches='tight');fig.savefig(out/'model_workflow.png',dpi=170,bbox_inches='tight')
