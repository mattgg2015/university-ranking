import json
import math

SHORT_NAMES = {
    "Massachusetts Institute of Technology": "MIT",
    "California Institute of Technology": "Caltech",
    "Columbia University in the City of New York": "Columbia",
    "University of California, Berkeley": "UC Berkeley",
    "University of California, Los Angeles": "UCLA",
    "University of California, San Diego": "UC San Diego",
    "University of California, Davis": "UC Davis",
    "University of California, Irvine": "UC Irvine",
    "University of California, Santa Barbara": "UC Santa Barbara",
    "University of Michigan - Ann Arbor": "Michigan",
    "University of Texas at Austin": "UT Austin",
    "University of North Carolina at Chapel Hill": "UNC Chapel Hill",
    "University of Illinois at Urbana-Champaign": "UIUC",
    "University of Wisconsin - Madison": "Wisconsin",
    "Georgia Institute of Technology": "Georgia Tech",
    "Washington University in St. Louis": "WashU",
    "University of Notre Dame": "Notre Dame",
    "University of Southern California": "USC",
    "University of Virginia": "UVA",
    "University of Pennsylvania": "Penn",
    "Johns Hopkins University": "Johns Hopkins",
    "Carnegie Mellon University": "Carnegie Mellon",
    "University of Florida": "Florida",
    "University of Chicago": "UChicago",
    "Vanderbilt University": "Vanderbilt",
    "Northwestern University": "Northwestern",
    "Emory University": "Emory",
    "Georgetown University": "Georgetown",
    "New York University": "NYU",
    "Boston College": "Boston College",
    "Tufts University": "Tufts",
    "Rice University": "Rice",
    "Brown University": "Brown",
    "Dartmouth College": "Dartmouth",
    "Cornell University": "Cornell",
    "Duke University": "Duke",
    "Princeton University": "Princeton",
    "Harvard University": "Harvard",
    "Stanford University": "Stanford",
    "Yale University": "Yale",
}


with open("cross_admit_data.json") as f:
    raw = json.load(f)

# Get schools from the data itself
schools = sorted({m["school_a"] for m in raw} | {m["school_b"] for m in raw})
school_idx = {s: i for i, s in enumerate(schools)}
n = len(schools)

# Parse matchups, estimate sample sizes from confidence intervals
matchups = []
for m in raw:
    if m["pct_a"] is None:
        continue
    i, j = school_idx[m["school_a"]], school_idx[m["school_b"]]
    pct = m["pct_a"] / 100.0

    ci_width = (m["ci_high_a"] - m["ci_low_a"]) / 100.0
    if ci_width > 0 and 0 < pct < 1:
        sample_n = pct * (1 - pct) * (1.96 / (ci_width / 2)) ** 2
    else:
        sample_n = 1.0
    matchups.append((i, j, pct, max(sample_n, 1.0)))

# Normalize weights
mean_n = sum(m[3] for m in matchups) / len(matchups)
matchups = [(i, j, pct, w / mean_n) for i, j, pct, w in matchups]

# Count wins/losses (95% CI doesn't overlap 50%)
wins, losses = [0] * n, [0] * n
for m in raw:
    if m["pct_a"] is None:
        continue
    i, j = school_idx[m["school_a"]], school_idx[m["school_b"]]
    if m["ci_low_a"] > 50:
        wins[i] += 1
        losses[j] += 1
    elif m["ci_high_a"] < 50:
        wins[j] += 1
        losses[i] += 1

# Elo with narrowing Gaussian window
ratings = [1500.0] * n
sigma = 40.0

for _ in range(10000):
    ranked = sorted(range(n), key=lambda x: -ratings[x])
    rank_of = {s: r for r, s in enumerate(ranked)}

    deltas = [0.0] * n
    for i, j, actual, weight in matchups:
        dist = abs(rank_of[i] - rank_of[j])
        proximity = math.exp(-dist**2 / (2 * sigma**2))

        expected = 1 / (1 + 10 ** ((ratings[j] - ratings[i]) / 400))
        update = 4 * weight * proximity * (actual - expected)
        deltas[i] += update
        deltas[j] -= update

    max_change = 0
    for s in range(n):
        change = 0.1 * deltas[s]
        ratings[s] += change
        max_change = max(max_change, abs(change))

    sigma = max(3.0, sigma * 0.995)
    if max_change < 0.001:
        break

# Output
ranked = sorted(range(n), key=lambda x: -ratings[x])
print(f"{'Rank':<6}{'School':<22}{'W-L':<10}{'Elo':>8}")
print("-" * 46)
for rank, idx in enumerate(ranked, 1):
    name = SHORT_NAMES.get(schools[idx], schools[idx])
    print(f"{rank:<6}{name:<22}{wins[idx]}-{losses[idx]:<8}{ratings[idx]:>8.1f}")
