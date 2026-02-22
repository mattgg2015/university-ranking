import requests
from bs4 import BeautifulSoup
import re
import json
import time
import itertools

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


def fetch_matchup(school_a, school_b):
    url = "https://www.parchment.com/c/college/tools/college-cross-admit-comparison.php"
    resp = requests.get(url, params={"compare": school_a, "with": school_b})
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    divs = soup.find_all("div", class_="college-matchup-comparison")
    if len(divs) < 2:
        return None

    pct_span = divs[0].find("span", class_="percentage")
    if not pct_span:
        return None
    pct = float(pct_span.get_text(strip=True).replace("%", ""))

    ci = re.search(r'confidence interval:\s*([\d.]+)%\s*to\s*([\d.]+)%', divs[0].get_text())
    ci_low, ci_high = (float(ci.group(1)), float(ci.group(2))) if ci else (None, None)

    return {"pct_a": pct, "ci_low_a": ci_low, "ci_high_a": ci_high}


if __name__ == "__main__":
    # Load existing for resume capability
    try:
        with open("cross_admit_data.json") as f:
            results = json.load(f)
        done = {(r["school_a"], r["school_b"]) for r in results}
    except FileNotFoundError:
        results, done = [], set()

    pairs = [(a, b) for a, b in itertools.combinations(SCHOOLS, 2) if (a, b) not in done]
    print(f"{len(results)} done, {len(pairs)} remaining")

    for i, (a, b) in enumerate(pairs):
        print(f"[{len(results) + 1}/780] {a[:20]} vs {b[:20]}... ", end="", flush=True)
        try:
            data = fetch_matchup(a, b)
            if data:
                print(f"{data['pct_a']}%")
                results.append({"school_a": a, "school_b": b, **data})
            else:
                print("no data")
                results.append({"school_a": a, "school_b": b, "pct_a": None, "ci_low_a": None, "ci_high_a": None})
        except Exception as e:
            print(f"error: {e}")
            results.append({"school_a": a, "school_b": b, "pct_a": None, "ci_low_a": None, "ci_high_a": None})

        with open("cross_admit_data.json", "w") as f:
            json.dump(results, f, indent=2)
        time.sleep(1)

    print(f"\nDone. {sum(1 for r in results if r['pct_a'])} with data, {sum(1 for r in results if not r['pct_a'])} without")
