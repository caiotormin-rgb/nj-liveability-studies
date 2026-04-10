"""
NJ Quality of Life Index Analysis — Phase 3
Methods: Weighted Z-Score (A) + PCA (B)
"""
import duckdb, pandas as pd, numpy as np, os, copy
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/db/nj_pipeline.duckdb')
OUT_DIR = os.path.join(os.path.dirname(__file__), '../NJ_Analysis_Vault/EDA Findings')
PROC_DIR = os.path.join(os.path.dirname(__file__), '../data/processed')
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(PROC_DIR, exist_ok=True)

# ── 1. Load data ──────────────────────────────────────────────────────────────
con = duckdb.connect(DB_PATH, read_only=True)
scorecard = con.execute('SELECT * FROM v_zipcode_scorecard').df()
afford    = con.execute('SELECT zip_code, home_price_to_income_ratio FROM v_affordability_index').df()
flood     = con.execute('SELECT zip_code, pct_high_risk_flood_zone FROM fema_flood_summary').df()
flood['zip_code'] = flood['zip_code'].astype(str).str.zfill(5)
con.close()

df = scorecard.merge(afford, on='zip_code', how='left').merge(flood, on='zip_code', how='left')
print(f'Master matrix: {len(df)} ZIPs')

# ── 2. Domain config ──────────────────────────────────────────────────────────
DOMAINS = {
    'Economic Security':    {'weight': 0.30, 'vars': {'income_median_hh': +1, 'poverty_rate': -1, 'unemployment_rate_acs': -1}},
    'Housing Affordability':{'weight': 0.20, 'vars': {'home_price_to_income_ratio': -1, 'rent_burden_30plus_pct': -1}},
    'Education':            {'weight': 0.15, 'vars': {'pct_bachelors_plus': +1}},
    'Health & Environment': {'weight': 0.20, 'vars': {'obesity_pct': -1, 'smoking_pct': -1, 'physical_inactivity_pct': -1, 'uninsured_pct': -1}},
    'Flood & Climate Risk': {'weight': 0.10, 'vars': {'pct_high_risk_flood_zone': -1}},
    'Mobility':             {'weight': 0.05, 'vars': {'avg_commute_minutes': -1, 'pct_wfh': +1, 'pct_transit_commute': +1}},
}
all_vars = [v for d in DOMAINS.values() for v in d['vars']]

# ── 3. Impute & filter ────────────────────────────────────────────────────────
df['pct_high_risk_flood_zone'] = df['pct_high_risk_flood_zone'].fillna(0)
for v in all_vars:
    if df[v].isnull().any():
        n = df[v].isnull().sum()
        med = df[v].median()
        df[v] = df[v].fillna(med)
        print(f'  Imputed {n} missing in {v} with median={med:.2f}')

df = df[df['pop_total'] >= 500].copy().reset_index(drop=True)
print(f'After pop≥500 filter: {len(df)} ZIPs\n')

# ── 4. Method A: Weighted Z-Score ─────────────────────────────────────────────
def compute_qol(df, domains):
    composite = np.zeros(len(df))
    domain_scores = {}
    for name, cfg in domains.items():
        zs = []
        for col, dirn in cfg['vars'].items():
            z = (df[col] - df[col].mean()) / df[col].std()
            zs.append(dirn * z)
        ds = np.mean(zs, axis=0)
        domain_scores[name] = ds
        composite += cfg['weight'] * ds
    c_min, c_max = composite.min(), composite.max()
    qol = 100 * (composite - c_min) / (c_max - c_min)
    out = df[['zip_code', 'city', 'zillow_county', 'pop_total']].copy()
    out['qol_score'] = qol
    out['qol_rank'] = out['qol_score'].rank(ascending=False, na_option='bottom').astype(int)
    for name, ds in domain_scores.items():
        key = 'score_' + name.lower().replace(' & ', '_').replace(' ', '_')
        d_min, d_max = ds.min(), ds.max()
        out[key] = 100*(ds-d_min)/(d_max-d_min) if d_max > d_min else 50.0
    return out.sort_values('qol_rank').reset_index(drop=True)

qol_a = compute_qol(df, DOMAINS)
subscore_cols = [c for c in qol_a.columns if c.startswith('score_')]

print('=== TOP 20 — Weighted Z-Score QoL ===')
print(qol_a.head(20)[['qol_rank','zip_code','city','zillow_county','qol_score']].to_string(index=False))
print()
print('=== BOTTOM 20 — Weighted Z-Score QoL ===')
print(qol_a.tail(20)[['qol_rank','zip_code','city','zillow_county','qol_score']].to_string(index=False))

# ── 5. Method B: PCA ──────────────────────────────────────────────────────────
X = df[all_vars].copy()
for name, cfg in DOMAINS.items():
    for col, dirn in cfg['vars'].items():
        if dirn == -1:
            X[col] = -X[col]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA()
pca.fit(X_scaled)
cumvar = np.cumsum(pca.explained_variance_ratio_)
n70 = np.argmax(cumvar >= 0.70) + 1
print(f'\nPCA: PC1 explains {pca.explained_variance_ratio_[0]:.1%}, '
      f'{n70} components for 70% variance')

# PC1 loadings
loadings = pd.Series(pca.components_[0], index=all_vars).sort_values()
print('\nPC1 Loadings:')
print(loadings.to_string())

pc1 = pca.transform(X_scaled)[:, 0]
qol_b = df[['zip_code', 'city', 'zillow_county', 'pop_total']].copy()
qol_b['qol_pca_score'] = 100 * (pc1 - pc1.min()) / (pc1.max() - pc1.min())
qol_b['qol_pca_rank'] = qol_b['qol_pca_score'].rank(ascending=False).astype(int)
qol_b = qol_b.sort_values('qol_pca_rank').reset_index(drop=True)

print('\n=== TOP 20 — PCA QoL ===')
print(qol_b.head(20)[['qol_pca_rank','zip_code','city','zillow_county','qol_pca_score']].to_string(index=False))
print()
print('=== BOTTOM 20 — PCA QoL ===')
print(qol_b.tail(20)[['qol_pca_rank','zip_code','city','zillow_county','qol_pca_score']].to_string(index=False))

# ── 6. Method agreement ───────────────────────────────────────────────────────
combined = qol_a.merge(qol_b[['zip_code','qol_pca_score','qol_pca_rank']], on='zip_code')
rho, pval = spearmanr(combined['qol_rank'], combined['qol_pca_rank'])
print(f'\nMethod rank correlation: ρ = {rho:.3f} (p={pval:.2e})')

print('\n=== TOP 15 RANK DISAGREEMENTS ===')
combined['rank_diff'] = (combined['qol_rank'] - combined['qol_pca_rank']).abs()
print(combined.nlargest(15, 'rank_diff')[['zip_code','city','zillow_county','qol_rank','qol_pca_rank','rank_diff']].to_string(index=False))

# ── 7. Validation against known towns ────────────────────────────────────────
total = len(combined)
print(f'\n=== VALIDATION (n={total}) ===')
print('Expected HIGH scorers:')
for city in ['Princeton','Rumson','Westfield','Summit','Montclair','Ridgewood','Short Hills','Chatham']:
    rows = combined[combined['city'].str.contains(city, case=False, na=False)]
    for _, r in rows.iterrows():
        pct = 100 * (1 - r.qol_rank/total)
        print(f'  {r.city:22s} ({r.zip_code}) rank {r.qol_rank:3d}/{total} ({pct:.0f}th pctile)')

print('Expected LOW scorers:')
for city in ['Camden','Trenton','Paterson','Atlantic City','Newark','Asbury Park','Bridgeton']:
    rows = combined[combined['city'].str.contains(city, case=False, na=False)]
    for _, r in rows.iterrows():
        pct = 100 * (1 - r.qol_rank/total)
        print(f'  {r.city:22s} ({r.zip_code}) rank {r.qol_rank:3d}/{total} ({pct:.0f}th pctile)')

# ── 8. Sensitivity analysis ───────────────────────────────────────────────────
np.random.seed(42)
n_trials = 200
rank_matrix = np.zeros((len(df), n_trials))

def perturb_weights(domains, pct=0.10):
    p = copy.deepcopy(domains)
    for d in p.values():
        d['weight'] *= (1 + np.random.uniform(-pct, pct))
    total = sum(d['weight'] for d in p.values())
    for d in p.values():
        d['weight'] /= total
    return p

zip_order = df['zip_code'].values
for i in range(n_trials):
    trial = compute_qol(df, perturb_weights(DOMAINS))
    rank_lookup = trial.set_index('zip_code')['qol_rank']
    rank_matrix[:, i] = [rank_lookup[z] for z in zip_order]

rank_std = pd.Series(rank_matrix.std(axis=1), index=zip_order)
print(f'\nSensitivity (±10% weight perturbation, {n_trials} trials):')
print(f'  Median rank std dev: {rank_std.median():.1f}')
print(f'  90th pct rank std dev: {rank_std.quantile(0.90):.1f}')
unstable = rank_std.nlargest(10).reset_index()
unstable.columns = ['zip_code', 'rank_std']
unstable = unstable.merge(df[['zip_code','city']], on='zip_code')
print('\nMost rank-unstable ZIPs:')
print(unstable[['zip_code','city','rank_std']].to_string(index=False))

# ── 9. County summary ─────────────────────────────────────────────────────────
county_summary = qol_a.groupby('zillow_county').agg(
    n_zips=('zip_code','count'),
    avg_qol=('qol_score','mean'),
    median_qol=('qol_score','median'),
    min_qol=('qol_score','min'),
    max_qol=('qol_score','max'),
).round(1).sort_values('median_qol', ascending=False)
print('\n=== QoL by County ===')
print(county_summary.to_string())

# ── 10. Plots ─────────────────────────────────────────────────────────────────
plt.rcParams.update({'figure.dpi': 150})

# Scree plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
n_show = 12
ax1.bar(range(1,n_show+1), pca.explained_variance_ratio_[:n_show]*100, color='steelblue')
ax1.set(xlabel='PC', ylabel='Variance (%)', title='Scree Plot', xticks=range(1,n_show+1))
ax2.plot(range(1,n_show+1), cumvar[:n_show]*100, 'o-', color='steelblue')
ax2.axhline(70, ls='--', color='orange', label='70%')
ax2.axhline(80, ls='--', color='red', label='80%')
ax2.set(xlabel='# Components', ylabel='Cumulative %', title='Cumulative Variance', xticks=range(1,n_show+1))
ax2.legend()
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/qol_pca_scree.png', bbox_inches='tight')
plt.close()
print('Saved qol_pca_scree.png')

# Rank agreement
fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(combined['qol_rank'], combined['qol_pca_rank'], alpha=0.35, s=12, color='steelblue')
lim = combined['qol_rank'].max()
ax.plot([1,lim],[1,lim],'r--', alpha=0.5, label='Perfect agreement')
ax.set(xlabel='Rank (Z-Score)', ylabel='Rank (PCA)', title=f'Method Agreement: ρ={rho:.3f}')
ax.legend()
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/qol_rank_agreement.png', bbox_inches='tight')
plt.close()
print('Saved qol_rank_agreement.png')

# Top 20
top20 = qol_a.head(20).copy()
top20['label'] = top20['zip_code'] + '\n' + top20['city'].str[:14]
fig, ax = plt.subplots(figsize=(14, 5))
bars = ax.barh(top20['label'][::-1], top20['qol_score'][::-1], color='steelblue')
ax.set(xlabel='QoL Score (0–100)', title='Top 20 NJ ZIP Codes — Quality of Life Index', xlim=(0,108))
for bar, score in zip(bars, top20['qol_score'][::-1]):
    ax.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2, f'{score:.1f}', va='center', fontsize=8)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/qol_top20.png', bbox_inches='tight')
plt.close()
print('Saved qol_top20.png')

# Bottom 20
bot20 = qol_a.tail(20).copy()
bot20['label'] = bot20['zip_code'] + '\n' + bot20['city'].str[:14]
fig, ax = plt.subplots(figsize=(14, 5))
bars = ax.barh(bot20['label'][::-1], bot20['qol_score'][::-1], color='tomato')
ax.set(xlabel='QoL Score (0–100)', title='Bottom 20 NJ ZIP Codes — Quality of Life Index', xlim=(0,108))
for bar, score in zip(bars, bot20['qol_score'][::-1]):
    ax.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2, f'{score:.1f}', va='center', fontsize=8)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/qol_bottom20.png', bbox_inches='tight')
plt.close()
print('Saved qol_bottom20.png')

# Distribution
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(qol_a['qol_score'], bins=40, color='steelblue', edgecolor='white', alpha=0.85)
ax.axvline(qol_a['qol_score'].median(), color='orange', ls='--', label=f'Median: {qol_a.qol_score.median():.1f}')
ax.set(xlabel='QoL Score', ylabel='ZIP Codes', title='NJ QoL Score Distribution')
ax.legend()
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/qol_distribution.png', bbox_inches='tight')
plt.close()
print('Saved qol_distribution.png')

# Domain correlations
fig, ax = plt.subplots(figsize=(9, 7))
corr = qol_a[subscore_cols].corr()
labels = [c.replace('score_','').replace('_',' ').title() for c in subscore_cols]
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdYlGn', xticklabels=labels, yticklabels=labels,
            ax=ax, vmin=-1, vmax=1, center=0)
ax.set_title('Domain Subscore Correlations')
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/qol_domain_correlations.png', bbox_inches='tight')
plt.close()
print('Saved qol_domain_correlations.png')

# County chart
fig, ax = plt.subplots(figsize=(10, 6))
cs = county_summary.sort_values('median_qol')
colors = ['steelblue' if v >= county_summary['median_qol'].median() else 'tomato' for v in cs['median_qol']]
ax.barh(cs.index, cs['median_qol'], color=colors)
ax.axvline(county_summary['median_qol'].median(), ls='--', color='orange', alpha=0.7, label='State median')
ax.set(xlabel='Median QoL Score', title='Median QoL Score by County')
ax.legend()
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/qol_by_county.png', bbox_inches='tight')
plt.close()
print('Saved qol_by_county.png')

# ── 11. Save outputs ──────────────────────────────────────────────────────────
output = qol_a.merge(qol_b[['zip_code','qol_pca_score','qol_pca_rank']], on='zip_code')
raw_extra = ['zip_code','income_median_hh','poverty_rate','unemployment_rate_acs',
             'pct_bachelors_plus','homeownership_rate','home_price_to_income_ratio',
             'rent_burden_30plus_pct','obesity_pct','smoking_pct',
             'physical_inactivity_pct','uninsured_pct','pct_high_risk_flood_zone',
             'avg_commute_minutes','pct_wfh','pct_transit_commute']
output = output.merge(df[raw_extra], on='zip_code')
parquet_path = f'{PROC_DIR}/qol_scores.parquet'
output.to_parquet(parquet_path, index=False)
print(f'\nSaved {parquet_path} ({len(output)} rows, {len(output.columns)} cols)')

# Load into DuckDB
con_rw = duckdb.connect(DB_PATH)
con_rw.execute('DROP TABLE IF EXISTS qol_scores')
con_rw.execute(f"CREATE TABLE qol_scores AS SELECT * FROM read_parquet('{parquet_path}')")
cnt = con_rw.execute('SELECT COUNT(*) FROM qol_scores').fetchone()[0]
con_rw.close()
print(f'Created qol_scores table in DuckDB ({cnt} rows)')

# ── 12. Final summary ─────────────────────────────────────────────────────────
print('\n' + '='*60)
print('QoL INDEX SUMMARY')
print('='*60)
print(f'ZIP codes analyzed: {len(output)}')
print(f'Score range:  {output.qol_score.min():.1f} – {output.qol_score.max():.1f}')
print(f'Mean: {output.qol_score.mean():.1f}   Median: {output.qol_score.median():.1f}')
print()
tiers = [(80,100,'Elite'),(60,80,'High'),(40,60,'Mid'),(20,40,'Low'),(0,20,'Distressed')]
for lo, hi, label in tiers:
    n = ((output.qol_score >= lo) & (output.qol_score < hi)).sum() if lo>0 else (output.qol_score < hi).sum()
    if hi == 100: n = (output.qol_score >= lo).sum()
    print(f'  {label:12s} ({lo:2d}–{hi:3d}): {n:3d} ZIPs')
print(f'\nMethod correlation (Spearman): ρ = {rho:.3f}')
print(f'Sensitivity (median rank std):  {rank_std.median():.1f} positions')
