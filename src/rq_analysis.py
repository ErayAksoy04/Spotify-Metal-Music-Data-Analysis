import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf


# ---------------------------
# Settings
# ---------------------------
CSV_PATH = "metal_tracks_with_audio.csv"
OUT_DIR = "../.venv/outputs_rq2"
ALPHA = 0.05

FEATURES = [
    "acousticness", "danceability", "energy", "instrumentalness",
    "liveness", "loudness", "speechiness", "tempo", "valence"
]

# Optional: choose some "similar genre" pairs to compare (you can add/remove)
PAIRWISE_GENRE_PAIRS = [
    ("Death Metal", "Black Metal"),
    ("Doom Metal", "Post-metal"),
    ("Thrash Metal", "Speed Metal"),
    ("Industrial Metal", "Alternative Metal"),
]


# ---------------------------
# Helpers
# ---------------------------
def ensure_out_dir(path: str):
    os.makedirs(path, exist_ok=True)

def coerce_numeric(df: pd.DataFrame, cols):
    """Convert columns to numeric robustly, forcing invalid -> NaN."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def latex_table_no_jinja2(df: pd.DataFrame, caption: str, label: str) -> str:
    """
    Simple LaTeX table generator (no pandas.to_latex, no jinja2).
    Produces a tabular with column headers and rows.
    """
    def esc(s):
        s = str(s)
        for a, b in [("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#")]:
            s = s.replace(a, b)
        return s

    cols = list(df.columns)
    header = " & ".join(esc(c) for c in cols) + r" \\ \hline"
    rows = []
    for _, row in df.iterrows():
        rows.append(" & ".join(esc(x) for x in row.values) + r" \\")
    body = "\n".join(rows)

    col_fmt = "|".join(["l"] * len(cols))
    return f"""
\\begin{{table}}[t]
\\centering
\\caption{{{esc(caption)}}}
\\label{{{esc(label)}}}
\\begin{{tabular}}{{|{col_fmt}|}}
\\hline
{header}
{body}
\\hline
\\end{{tabular}}
\\end{{table}}
""".strip()

def bonferroni(pvals: np.ndarray) -> np.ndarray:
    m = len(pvals)
    return np.minimum(pvals * m, 1.0)

def eta_squared_anova(model) -> float:
    """
    Eta-squared = SSeffect / SStotal using ANOVA table.
    Works for one-way ANOVA (feature ~ C(main_genre)).
    """
    aov = sm.stats.anova_lm(model, typ=2)
    ss_effect = aov.loc["C(main_genre)", "sum_sq"]
    ss_total = ss_effect + aov.loc["Residual", "sum_sq"]
    return float(ss_effect / ss_total) if ss_total > 0 else np.nan


# ---------------------------
# Main
# ---------------------------
def main():
    ensure_out_dir(OUT_DIR)

    # 1) Load
    df = pd.read_csv(CSV_PATH)

    # 2) Basic cleaning / numeric coercion (fixes valence aggregation errors)
    numeric_cols = ["popularity", "key", "mode"] + FEATURES
    df = coerce_numeric(df, numeric_cols)

    # Keep only mode in {0,1} when available
    df["mode"] = df["mode"].where(df["mode"].isin([0, 1]), np.nan)

    # Drop rows missing essential fields
    df = df.dropna(subset=["main_genre", "sub_genre", "popularity"])
    # Drop rows where ALL features are missing
    df = df.dropna(subset=FEATURES, how="all")

    # Save cleaned dataset
    clean_path = os.path.join(OUT_DIR, "metal_tracks_clean.csv")
    df.to_csv(clean_path, index=False)

    # ---------------------------
    # A) One-way ANOVA per feature (feature ~ main_genre)
    # ---------------------------
    anova_rows = []
    for feat in FEATURES:
        d = df.dropna(subset=[feat, "main_genre"]).copy()
        if d["main_genre"].nunique() < 2:
            continue

        model = smf.ols(f"{feat} ~ C(main_genre)", data=d).fit()
        aov = sm.stats.anova_lm(model, typ=2)

        F = float(aov.loc["C(main_genre)", "F"])
        p = float(aov.loc["C(main_genre)", "PR(>F)"])
        eta2 = eta_squared_anova(model)

        anova_rows.append({
            "feature": feat,
            "n": len(d),
            "k_genres": int(d["main_genre"].nunique()),
            "F": F,
            "p_value": p,
            "eta_squared": eta2
        })

    anova_df = pd.DataFrame(anova_rows).sort_values("p_value")
    anova_df.to_csv(os.path.join(OUT_DIR, "anova_results.csv"), index=False)

    # LaTeX ANOVA table (top features)
    anova_top = anova_df.copy()
    anova_top["p_value"] = anova_top["p_value"].map(lambda x: f"{x:.3e}")
    anova_top["F"] = anova_top["F"].map(lambda x: f"{x:.3f}")
    anova_top["eta_squared"] = anova_top["eta_squared"].map(lambda x: f"{x:.3f}")

    anova_tex = latex_table_no_jinja2(
        anova_top[["feature", "n", "k_genres", "F", "p_value", "eta_squared"]],
        caption="One-way ANOVA results by feature (feature ~ main genre).",
        label="tab:anova_features"
    )
    with open(os.path.join(OUT_DIR, "anova_table.tex"), "w", encoding="utf-8") as f:
        f.write(anova_tex)

    # ---------------------------
    # B) Post-hoc pairwise t-tests for selected genre pairs (per feature)
    # ---------------------------
    posthoc_rows = []
    for (g1, g2) in PAIRWISE_GENRE_PAIRS:
        dpair = df[df["main_genre"].isin([g1, g2])].copy()
        if dpair["main_genre"].nunique() < 2:
            continue

        for feat in FEATURES:
            x = dpair.loc[dpair["main_genre"] == g1, feat].dropna().values
            y = dpair.loc[dpair["main_genre"] == g2, feat].dropna().values
            if len(x) < 10 or len(y) < 10:
                continue

            # Welch t-test (no equal-variance assumption)
            t, p = stats.ttest_ind(x, y, equal_var=False)

            # Cohen's d (using pooled SD for interpretability)
            sx, sy = np.std(x, ddof=1), np.std(y, ddof=1)
            pooled = np.sqrt(((len(x)-1)*sx*sx + (len(y)-1)*sy*sy) / (len(x)+len(y)-2))
            d_eff = (np.mean(x) - np.mean(y)) / pooled if pooled > 0 else np.nan

            posthoc_rows.append({
                "genre_1": g1, "genre_2": g2, "feature": feat,
                "n1": len(x), "n2": len(y),
                "mean_1": float(np.mean(x)), "mean_2": float(np.mean(y)),
                "t_stat": float(t), "p_value": float(p),
                "cohens_d": float(d_eff)
            })

    posthoc_df = pd.DataFrame(posthoc_rows)

    # Bonferroni correction across ALL pairwise tests
    if len(posthoc_df) > 0:
        posthoc_df["p_bonf"] = bonferroni(posthoc_df["p_value"].values)
        posthoc_df = posthoc_df.sort_values("p_bonf")
        posthoc_df.to_csv(os.path.join(OUT_DIR, "posthoc_pairwise.csv"), index=False)

        # LaTeX: only the most significant 15 rows
        ph = posthoc_df.head(15).copy()
        ph["p_value"] = ph["p_value"].map(lambda x: f"{x:.3e}")
        ph["p_bonf"] = ph["p_bonf"].map(lambda x: f"{x:.3e}")
        ph["t_stat"] = ph["t_stat"].map(lambda x: f"{x:.3f}")
        ph["cohens_d"] = ph["cohens_d"].map(lambda x: f"{x:.3f}")
        ph["mean_1"] = ph["mean_1"].map(lambda x: f"{x:.3f}")
        ph["mean_2"] = ph["mean_2"].map(lambda x: f"{x:.3f}")

        posthoc_tex = latex_table_no_jinja2(
            ph[["genre_1","genre_2","feature","n1","n2","mean_1","mean_2","t_stat","p_value","p_bonf","cohens_d"]],
            caption="Selected pairwise comparisons (Welch t-test) with Bonferroni correction.",
            label="tab:posthoc_pairs"
        )
        with open(os.path.join(OUT_DIR, "posthoc_table.tex"), "w", encoding="utf-8") as f:
            f.write(posthoc_tex)

    # ---------------------------
    # C) Chi-square: mode (major/minor) vs main_genre
    # ---------------------------
    mode_df = df.dropna(subset=["mode", "main_genre"]).copy()
    # contingency: rows=genre, cols=mode
    contingency = pd.crosstab(mode_df["main_genre"], mode_df["mode"])
    # ensure both columns exist
    for col in [0.0, 1.0]:
        if col not in contingency.columns:
            contingency[col] = 0
    contingency = contingency[[0.0, 1.0]]  # minor, major

    chi2, p_chi, dof, expected = stats.chi2_contingency(contingency.values)
    chi_summary = pd.DataFrame([{
        "chi2": chi2, "dof": dof, "p_value": p_chi,
        "n": int(contingency.values.sum())
    }])
    chi_summary.to_csv(os.path.join(OUT_DIR, "chi_square_mode_vs_genre.csv"), index=False)

    # Also export mode proportions by genre
    mode_props = contingency.div(contingency.sum(axis=1), axis=0).rename(columns={0.0:"minor_prop", 1.0:"major_prop"})
    mode_props.to_csv(os.path.join(OUT_DIR, "mode_proportions_by_genre.csv"))

    # Plot: stacked proportions
    plt.figure(figsize=(12, 6))
    plt.bar(mode_props.index, mode_props["minor_prop"], label="Minor (0)")
    plt.bar(mode_props.index, mode_props["major_prop"], bottom=mode_props["minor_prop"], label="Major (1)")
    plt.xticks(rotation=90)
    plt.ylabel("Proportion")
    plt.title("Major vs Minor Proportions by Main Genre")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "mode_stacked_proportions.png"), dpi=200)
    plt.close()

    # ---------------------------
    # D) Regression: popularity ~ features + main_genre dummies
    # ---------------------------
    reg_df = df.dropna(subset=["popularity"] + FEATURES + ["main_genre"]).copy()

    # Build formula: popularity ~ features + C(main_genre)
    formula = "popularity ~ " + " + ".join(FEATURES) + " + C(main_genre)"
    reg_model = smf.ols(formula, data=reg_df).fit()

    # Save full summary text
    with open(os.path.join(OUT_DIR, "regression_summary.txt"), "w", encoding="utf-8") as f:
        f.write(reg_model.summary().as_text())

    # Save compact coefficient table
    coef = reg_model.params.to_frame("beta")
    coef["p_value"] = reg_model.pvalues
    coef["std_err"] = reg_model.bse
    coef = coef.reset_index().rename(columns={"index": "term"})
    coef.to_csv(os.path.join(OUT_DIR, "regression_coefficients.csv"), index=False)

    # Simple LaTeX for top 20 most significant terms
    coef2 = coef.copy()
    coef2 = coef2.sort_values("p_value").head(20)
    coef2["beta"] = coef2["beta"].map(lambda x: f"{x:.4f}")
    coef2["std_err"] = coef2["std_err"].map(lambda x: f"{x:.4f}")
    coef2["p_value"] = coef2["p_value"].map(lambda x: f"{x:.3e}")

    reg_tex = latex_table_no_jinja2(
        coef2[["term", "beta", "std_err", "p_value"]],
        caption="Most significant regression coefficients for predicting popularity.",
        label="tab:regression_top"
    )
    with open(os.path.join(OUT_DIR, "regression_table.tex"), "w", encoding="utf-8") as f:
        f.write(reg_tex)

    # Optional: predicted vs actual plot
    y_true = reg_df["popularity"].values
    y_pred = reg_model.fittedvalues.values
    plt.figure(figsize=(6, 6))
    plt.scatter(y_true, y_pred, s=10)
    plt.xlabel("Actual Popularity")
    plt.ylabel("Predicted Popularity")
    plt.title("Popularity: Actual vs Predicted (Linear Regression)")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "popularity_actual_vs_pred.png"), dpi=200)
    plt.close()

    # Compute error metrics
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    metrics = pd.DataFrame([{
        "R2": float(reg_model.rsquared),
        "Adj_R2": float(reg_model.rsquared_adj),
        "MAE": float(mae),
        "RMSE": float(rmse),
        "n": int(len(reg_df))
    }])
    metrics.to_csv(os.path.join(OUT_DIR, "regression_metrics.csv"), index=False)

    print("Done. Outputs written to:", OUT_DIR)
    print("Clean dataset:", clean_path)


if __name__ == "__main__":
    main()
