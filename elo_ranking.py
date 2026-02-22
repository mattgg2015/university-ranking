import json
import math

SCHOOLS = [
    "Princeton University",
    "Massachusetts Institute of Technology",
    "Harvard University",
    "Stanford University",
    "Yale University",
    "University of Chicago",
    "Duke University",
    "Johns Hopkins University",
    "Northwestern University",
    "University of Pennsylvania",
    "California Institute of Technology",
    "Cornell University",
    "Brown University",
    "Dartmouth College",
    "Columbia University in the City of New York",
    "University of California, Berkeley",
    "University of California, Los Angeles",
    "Rice University",
    "Vanderbilt University",
    "Carnegie Mellon University",
    "University of Michigan - Ann Arbor",
    "University of Notre Dame",
    "Washington University in St. Louis",
    "Emory University",
    "Georgetown University",
    "University of North Carolina at Chapel Hill",
    "University of Virginia",
    "University of Southern California",
    "University of California, San Diego",
    "University of Florida",
    "University of Texas at Austin",
    "Georgia Institute of Technology",
    "New York University",
    "University of California, Davis",
    "University of California, Irvine",
    "Boston College",
    "Tufts University",
    "University of Illinois at Urbana-Champaign",
    "University of Wisconsin - Madison",
    "University of California, Santa Barbara",
]

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

# US News 2025 rankings for comparison
US_NEWS = {
    "Princeton": 1, "MIT": 2, "Harvard": 3, "Stanford": 4, "Yale": 5,
    "Caltech": 6, "Duke": 6, "Johns Hopkins": 6, "Northwestern": 6,
    "Penn": 10, "Cornell": 11, "UChicago": 11, "Brown": 13, "Columbia": 13,
    "Dartmouth": 15, "UCLA": 15, "UC Berkeley": 17, "Notre Dame": 18,
    "Rice": 18, "Vanderbilt": 18, "Carnegie Mellon": 21, "Michigan": 21,
    "WashU": 21, "Emory": 24, "Georgetown": 24, "UVA": 24, "UNC Chapel Hill": 27,
    "USC": 27, "UC San Diego": 29, "NYU": 30, "Florida": 30, "UT Austin": 30,
    "Georgia Tech": 33, "UC Davis": 33, "UC Irvine": 33, "UIUC": 33,
    "Boston College": 37, "Tufts": 37, "UC Santa Barbara": 39, "Wisconsin": 39,
}


def run():
    with open("cross_admit_data.json") as f:
        raw = json.load(f)

    school_idx = {s: i for i, s in enumerate(SCHOOLS)}
    n = len(SCHOOLS)

    # Parse matchups, estimate sample sizes from confidence intervals
    matchups = []
    for m in raw:
        if m["pct_a"] is None:
            continue
        i, j = school_idx[m["school_a"]], school_idx[m["school_b"]]
        pct = m["pct_a"] / 100.0

        # Back-calculate sample size from CI width using normal approximation
        ci_width = (m["ci_high_a"] - m["ci_low_a"]) / 100.0
        if ci_width > 0 and 0 < pct < 1:
            sample_n = pct * (1 - pct) * (1.96 / (ci_width / 2)) ** 2
        else:
            sample_n = 1.0
        matchups.append((i, j, pct, max(sample_n, 1.0)))

    # Normalize weights
    mean_n = sum(m[3] for m in matchups) / len(matchups)
    matchups = [(i, j, pct, w / mean_n) for i, j, pct, w in matchups]

    # Count wins/losses (statistically significant at 95%)
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

    # Elo with narrowing window
    # Starts comparing all schools, gradually focuses on nearby ranks
    ratings = [1500.0] * n
    sigma = 40.0  # window width in rank positions

    for round_num in range(10000):
        # Current rankings for proximity weighting
        ranked = sorted(range(n), key=lambda x: -ratings[x])
        rank_of = {s: r for r, s in enumerate(ranked)}

        deltas = [0.0] * n
        for i, j, actual, weight in matchups:
            # Gaussian weight: nearby ranks matter more as sigma shrinks
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

    # Build rankings
    ranked = sorted(range(n), key=lambda x: -ratings[x])

    print(f"{'Rank':<6}{'School':<22}{'W-L':<10}{'Elo':>8}{'US News':>10}{'Diff':>8}")
    print("-" * 64)
    for rank, idx in enumerate(ranked, 1):
        name = SHORT_NAMES.get(SCHOOLS[idx], SCHOOLS[idx])
        record = f"{wins[idx]}-{losses[idx]}"
        usn = US_NEWS.get(name, "—")
        diff = f"{'+' if usn > rank else ''}{usn - rank}" if isinstance(usn, int) else "—"
        print(f"{rank:<6}{name:<22}{record:<10}{ratings[idx]:>8.1f}{usn:>10}{diff:>8}")


if __name__ == "__main__":
    run()
