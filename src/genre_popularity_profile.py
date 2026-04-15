#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""See docstring inside for usage."""

import os
import time
import math
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Any

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = "1059db9faca445a5ba06fd78b78cee13"
CLIENT_SECRET = "d2ed39a90706443e920e0b42f4f03597"

MAX_TRACKS_PER_GENRE = 1000
LIMIT_PER_PAGE = 50
SLEEP_BETWEEN_CALLS = 0.15
EXCLUDE_ZERO_POP_IN_MEAN = True
MAKE_PLOTS = True

OUTPUT_DIR = "../.venv/output"
TRACKS_DIR = os.path.join(OUTPUT_DIR, "tracks_by_genre")
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")
os.makedirs(TRACKS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

def _safe_fname(name: str) -> str:
    bad = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for b in bad:
        name = name.replace(b, '_')
    return name.replace(' ', '_')

def connect_spotify() -> spotipy.Spotify:
    auth = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth)
    return sp

def fetch_tracks_for_genre(sp: spotipy.Spotify, genre: str, max_tracks: int = MAX_TRACKS_PER_GENRE):
    rows = []
    for offset in range(0, max_tracks, LIMIT_PER_PAGE):
        results = sp.search(q=f'genre:"{genre}"', type='track', limit=LIMIT_PER_PAGE, offset=offset)
        items = results.get('tracks', {}).get('items', [])
        if not items:
            break
        for t in items:
            rows.append({
                "track_id": t.get("id"),
                "track_name": t.get("name"),
                "artist_id": t.get("artists", [{}])[0].get("id") if t.get("artists") else None,
                "artist_name": t.get("artists", [{}])[0].get("name") if t.get("artists") else None,
                "album_id": t.get("album", {}).get("id"),
                "album_name": t.get("album", {}).get("name"),
                "release_date": t.get("album", {}).get("release_date"),
                "popularity": t.get("popularity", 0),
                "genre_query": genre
            })
        time.sleep(SLEEP_BETWEEN_CALLS)
    # de-dup by track_id
    seen, unique = set(), []
    for r in rows:
        tid = r.get("track_id")
        if tid and tid not in seen:
            unique.append(r); seen.add(tid)
    return unique

def robust_popularity_stats(pop_series: pd.Series) -> Dict[str, Any]:
    s = pd.to_numeric(pop_series, errors='coerce').dropna()
    n_total = len(pop_series)
    n_valid = len(s)
    n_zero = int((s == 0).sum())
    share_zero = (n_zero / n_valid) if n_valid else None
    out = {
        "count_total": n_total,
        "count_valid": n_valid,
        "count_zero": n_zero,
        "share_zero": share_zero,
        "mean_all": float(s.mean()) if n_valid else None,
        "median": float(s.median()) if n_valid else None,
        "p10": float(s.quantile(0.10)) if n_valid else None,
        "p25": float(s.quantile(0.25)) if n_valid else None,
        "p75": float(s.quantile(0.75)) if n_valid else None,
        "p90": float(s.quantile(0.90)) if n_valid else None,
        "iqr": float(s.quantile(0.75) - s.quantile(0.25)) if n_valid else None,
        "trimmed_mean_5": float(s.sort_values().iloc[math.floor(0.05*n_valid): math.ceil(0.95*n_valid)].mean()) if n_valid >= 20 else float(s.mean()) if n_valid else None
    }
    if EXCLUDE_ZERO_POP_IN_MEAN and n_valid:
        nz = s[s > 0]
        out["mean_nonzero"] = float(nz.mean()) if len(nz) else None
        out["share_nonzero"] = float(len(nz) / n_valid) if n_valid else None
    else:
        out["mean_nonzero"] = None
        out["share_nonzero"] = None
    return out

def plot_popularity(genre: str, df: pd.DataFrame) -> None:
    s = pd.to_numeric(df["popularity"], errors='coerce').dropna()
    if s.empty: return
    safe = _safe_fname(genre)
    # histogram
    plt.figure(); plt.hist(s, bins=20)
    plt.title(f"Popularity Histogram — {genre}")
    plt.xlabel("Popularity (0–100)"); plt.ylabel("Count")
    plt.savefig(os.path.join(PLOTS_DIR, f"{safe}_popularity_hist.png")); plt.close()
    # boxplot
    plt.figure(); plt.boxplot(s, vert=True)
    plt.title(f"Popularity Box — {genre}")
    plt.ylabel("Popularity (0–100)")
    plt.savefig(os.path.join(PLOTS_DIR, f"{safe}_popularity_box.png")); plt.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--genres", default="metal_genres.txt")
    parser.add_argument("--max-tracks", type=int, default=MAX_TRACKS_PER_GENRE)
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()

    if CLIENT_ID.startswith("YOUR_") or CLIENT_SECRET.startswith("YOUR_"):
        raise SystemExit("Please set CLIENT_ID and CLIENT_SECRET at the top of the script.")

    sp = connect_spotify()
    with open(args.genres, "r", encoding="utf-8") as f:
        genres = [g.strip() for g in f if g.strip()]

    summary = []
    for genre in genres:
        print(f"➡️  {genre}")
        rows = fetch_tracks_for_genre(sp, genre, max_tracks=args.max-tracks if hasattr(args, 'max-tracks') else args.max_tracks)
        df = pd.DataFrame(rows)
        df.to_csv(os.path.join(TRACKS_DIR, f"{_safe_fname(genre)}.csv"), index=False, encoding="utf-8")
        stats = robust_popularity_stats(df["popularity"] if "popularity" in df else pd.Series(dtype=float))
        summary.append({
            "genre": genre,
            "n_tracks_collected": int(stats.get("count_total") or 0),
            "n_popularity_valid": int(stats.get("count_valid") or 0),
            "n_popularity_zero": int(stats.get("count_zero") or 0),
            "share_zero": stats.get("share_zero"),
            "mean_pop_all": stats.get("mean_all"),
            "median_pop": stats.get("median"),
            "trimmed_mean_5": stats.get("trimmed_mean_5"),
            "mean_pop_nonzero": stats.get("mean_nonzero"),
            "share_nonzero": stats.get("share_nonzero"),
            "p10": stats.get("p10"),
            "p25": stats.get("p25"),
            "p75": stats.get("p75"),
            "p90": stats.get("p90"),
            "iqr": stats.get("iqr")
        })
        if MAKE_PLOTS and not args.no_plots:
            try: plot_popularity(genre, df)
            except Exception as e: print("Plot error:", e)
        time.sleep(SLEEP_BETWEEN_CALLS)

    out = pd.DataFrame(summary).sort_values(by=["mean_pop_all"], ascending=False)
    out_path = os.path.join(OUTPUT_DIR, "summary_genre_popularity.csv")
    out.to_csv(out_path, index=False, encoding="utf-8")
    print("\n✅ Done. Summary:", out_path)

if __name__ == "__main__":
    main()
