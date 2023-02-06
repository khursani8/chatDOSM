from autofaiss import build_index
import numpy as np
import pandas as pd

df = pd.read_csv("mappings.csv")
df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)
embeddings = np.stack( df["embeddings"], axis=0 )
index, index_infos = build_index(
    embeddings,
    "knn.index",
    "index_infos.json",
    save_on_disk=True
)
