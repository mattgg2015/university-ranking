# College Rankings by Revealed Preference

I noticed that US News rankings sometimes didn't match my notion of where students actually wanted to go. So I scraped [Parchment's cross-admit tool](https://www.parchment.com/c/college/tools/college-cross-admit-comparison.php), which shows what percentage of students choose each school when admitted to both. For example, [MIT vs Stanford](https://www.parchment.com/c/college/tools/college-cross-admit-comparison.php?compare=Massachusetts%20Institute%20of%20Technology&with=Stanford%20University) shows 62% pick MIT. We assume that students are rational students making informed decisions. 

## The Data

Parchment aggregates enrollment decisions from students who use their transcript service. For each pair of schools, they report the percentage choosing each side plus a 95% confidence interval. I collected all 780 pairwise matchups between 40 top schools, of which 757 had sufficient data.

## The Algorithm

I use an Elo rating system (like chess) adapted for this data. The core idea: if School A beats School B more than expected given their ratings, A's rating goes up and B's goes down.

The key modification is a **narrowing Gaussian window**. Since all matchups occur at the same time, then early on all matchups are weighted equally. But as ratings stabilize, matchups between similarly-ranked (peer) schools get exponentially more weighted than distant ones (via `exp(-distance² / 2σ²)` where σ shrinks from 40 to 3 over iterations). This prevents a blowout win against a much weaker school from distorting rankings among peers.

Matchups are also weighted by sample size, estimated from confidence interval width, as a comparison with 500 respondents provides more information more than one with 20.

## The Rankings

| Rank | School | W-L | Elo | US News | vs USN |
|------|--------|-----|-----|---------|--------|
| 1 | MIT | 32-0 | 1911 | 2 | +1 |
| 2 | Harvard | 35-1 | 1900 | 3 | +1 |
| 3 | Yale | 33-2 | 1821 | 5 | +2 |
| 4 | Stanford | 34-2 | 1820 | 4 | — |
| 5 | Princeton | 26-3 | 1751 | 1 | -4 |
| 6 | Columbia | 24-3 | 1744 | 13 | +7 |
| 7 | Penn | 14-6 | 1650 | 10 | +3 |
| 8 | Caltech | 10-5 | 1646 | 6 | -2 |
| 9 | UChicago | 19-6 | 1646 | 11 | +2 |
| 10 | Brown | 16-7 | 1646 | 13 | +3 |
| 11 | Dartmouth | 18-4 | 1639 | 15 | +4 |
| 12 | Duke | 14-8 | 1607 | 6 | -6 |
| 13 | UCLA | 20-9 | 1587 | 15 | +2 |
| 14 | Johns Hopkins | 16-9 | 1568 | 6 | -8 |
| 15 | Notre Dame | 11-7 | 1568 | 18 | +3 |
| 16 | Rice | 9-11 | 1558 | 18 | +2 |
| 17 | Northwestern | 14-12 | 1546 | 6 | -11 |
| 18 | UC Berkeley | 19-10 | 1542 | 17 | -1 |
| 19 | USC | 17-11 | 1529 | 27 | +8 |
| 20 | Michigan | 18-15 | 1513 | 21 | +1 |
| 21 | Vanderbilt | 7-16 | 1461 | 18 | -3 |
| 22 | Cornell | 9-16 | 1455 | 11 | -11 |
| 23 | WashU | 10-11 | 1454 | 21 | -2 |
| 24 | UT Austin | 9-11 | 1454 | 30 | +6 |
| 25 | Georgia Tech | 9-15 | 1431 | 33 | +8 |
| 26 | Carnegie Mellon | 5-21 | 1423 | 21 | -5 |
| 27 | UVA | 6-16 | 1422 | 24 | -3 |
| 28 | Georgetown | 6-15 | 1416 | 24 | -4 |
| 29 | UIUC | 3-15 | 1405 | 33 | +4 |
| 30 | Emory | 5-19 | 1373 | 24 | -6 |
| 31 | Tufts | 1-14 | 1357 | 37 | +6 |
| 32 | UNC Chapel Hill | 1-22 | 1302 | 27 | -5 |
| 33 | Wisconsin | 5-20 | 1298 | 39 | +6 |
| 34 | UC San Diego | 4-24 | 1274 | 29 | -5 |
| 35 | UC Irvine | 2-20 | 1267 | 33 | -2 |
| 36 | Florida | 1-13 | 1258 | 30 | -6 |
| 37 | Boston College | 2-18 | 1224 | 37 | — |
| 38 | NYU | 2-25 | 1183 | 30 | -8 |
| 39 | UC Davis | 1-19 | 1181 | 33 | -6 |
| 40 | UC Santa Barbara | 1-27 | 1171 | 39 | -1 |

**W-L**: Wins/losses where the 95% CI doesn't overlap 50% (statistically significant)

**vs USN**: Difference from US News 2025 ranking (positive = underrated by US News)

## Caveats

Cross-admit data conflates preference with affordability. A student picking UCLA over Northwestern might be choosing $15k/year over $80k/year, not making a quality judgment. Financial aid packages, geography, and major-specific fit all influence choices in ways that don't really generalize. However, no ranking system is perfect, and I feel that this ranking is closer to how high school students view relative value and prestige. 
