export function runSearch(state, opts) {
  const { q, confs, years, sort, allYearsCount } = opts;
  const allConfs = confs.length === 3;
  const allYears = years.length === allYearsCount && allYearsCount > 0;
  if (!q && allConfs && allYears) {
    return null;
  }

  let candidates;
  if (q && state.index) {
    candidates = state.index.search(q, { combineWith: "AND" });
  } else {
    candidates = state.papers.map(p => ({ ...p, score: 0 }));
  }

  const filtered = candidates.filter(p =>
    confs.includes(p.conference) && years.includes(p.year)
  );

  if (sort === "year-desc") {
    filtered.sort((a, b) => b.year - a.year);
  }
  return filtered;
}
