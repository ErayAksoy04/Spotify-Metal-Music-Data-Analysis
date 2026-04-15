import pandas as pd

df = pd.read_csv("metal_tracks_with_audio.csv")

genre_table = (
    df.groupby(["main_genre", "sub_genre"])
      .size()
      .reset_index(name="track_count")
      .sort_values(["main_genre", "sub_genre"])
)

latex_output = genre_table.to_latex(
    index=False,
    caption="Track Count per Main Genre and Subgenre",
    label="table:genre_subgenre",
    longtable=True,        # Çok satırlı tablo için ideal
    escape=False
)

with open("../docs/genre_subgenre_table.tex", "w", encoding="utf-8") as f:
    f.write(latex_output)

print("LaTeX table exported to genre_subgenre_table.tex")
