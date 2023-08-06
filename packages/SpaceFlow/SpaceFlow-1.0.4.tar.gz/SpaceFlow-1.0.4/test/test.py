import squidpy as sq
from SpaceFlow import SpaceFlow

adata = sq.datasets.seqfish()

sf = SpaceFlow.SpaceFlow(adata=adata)

sf.preprocessing_data(n_top_genes=3000)

print(sf.adata.var_names)