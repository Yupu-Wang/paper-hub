export function runSearch(state, opts) {
  const { q, author, confs, years, sort, allYearsCount } = opts;
  const noQuery = !q && !author;
  const allConfs = confs.length === 3;
  const allYears = years.length === allYearsCount && allYearsCount > 0;
  if (noQuery && allConfs && allYears) {
    return null;
  }

  let candidates;
  if (q && state.index) {
    candidates = state.index.search(q, { combineWith: "AND" });
  } else {
    candidates = state.papers.map(p => ({ ...p, score: 0 }));
  }

  const authorLower = author.toLowerCase();
  const filtered = candidates.filter(p =>
    confs.includes(p.conference) &&
    years.includes(p.year) &&
    (!author || p.authors.some(a => a.toLowerCase().includes(authorLower)))
  );

  if (sort === "year-desc") {
    filtered.sort((a, b) => b.year - a.year);
  }
  return filtered;
}
