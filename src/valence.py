import pandas as pd

df = pd.read_csv("metal_tracks_with_audio.csv")

# Valence kolonunu sayıya çevir (virgül vs. varsa onları da düzeltmek için)
df["valence"] = (
    df["valence"]
    .astype(str)                # her ihtimale karşı string yap
    .str.replace(",", ".", regex=False)  # olası , -> . dönüşümü
)
df["valence"] = pd.to_numeric(df["valence"], errors="coerce")

print(df["valence"].dtype)  # float64 olmalı

genre_valence = df.groupby("main_genre")["valence"].agg(
    mean="mean",
    median="median",
    std="std",
    count="count",
)

print(genre_valence)
