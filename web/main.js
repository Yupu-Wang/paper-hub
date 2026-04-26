import { renderResults } from "./render.js";
import { runSearch } from "./search.js";

const state = {
  papers: [],
  index: null,
  shardsTotal: 0,
  shardsLoaded: 0,
  yearsKnown: new Set(),
};

const progress = document.getElementById("progress");
const resultsEl = document.getElementById("results");
const yearFilter = document.getElementById("year-filter");
const searchEl = document.getElementById("search");
const sortEl = document.getElementById("sort");

function setProgress() {
  if (state.shardsLoaded < state.shardsTotal) {
    progress.textContent = `加载中… ${state.shardsLoaded}/${state.shardsTotal} (${state.papers.length} 篇)`;
  } else {
    progress.textContent = `已加载 ${state.papers.length} 篇`;
  }
}

function ensureIndex() {
  if (!state.index) {
    state.index = new MiniSearch({
      fields: ["title", "abstract", "authors_text", "keywords_text"],
      storeFields: ["id", "title", "authors", "abstract", "conference", "year", "url", "presentation"],
      searchOptions: { boost: { title: 2, keywords_text: 1.5 }, prefix: true, fuzzy: 0.1 },
    });
  }
}

function indexPapers(papers) {
  ensureIndex();
  const docs = papers.map(p => ({
    ...p,
    authors_text: p.authors.join(" "),
    keywords_text: (p.keywords || []).join(" "),
  }));
  state.index.addAll(docs);
}

function rebuildYearFilter() {
  const years = [...state.yearsKnown].sort((a, b) => b - a);
  yearFilter.innerHTML = "<legend>年份</legend>" + years.map(y =>
    `<label><input type="checkbox" name="year" value="${y}" checked> ${y}</label>`
  ).join("");
  yearFilter.querySelectorAll("input").forEach(i => i.addEventListener("change", triggerSearch));
}

async function loadShards() {
  const manifest = await fetch("data/manifest.json").then(r => r.json());
  state.shardsTotal = manifest.shards.length;
  setProgress();
  await Promise.all(manifest.shards.map(async (s) => {
    try {
      const data = await fetch(`data/${s.file}`).then(r => r.json());
      state.papers.push(...data.papers);
      state.yearsKnown.add(data.year);
      indexPapers(data.papers);
    } catch (e) {
      console.error("Failed to load shard", s.file, e);
    } finally {
      state.shardsLoaded += 1;
      setProgress();
      rebuildYearFilter();
      triggerSearch();
    }
  }));
}

function triggerSearch() {
  const q = searchEl.value.trim();
  const confs = [...document.querySelectorAll("input[name=conf]:checked")].map(i => i.value);
  const years = [...document.querySelectorAll("input[name=year]:checked")].map(i => +i.value);
  const sort = sortEl.value;
  const hits = runSearch(state, {
    q, confs, years, sort,
    allYearsCount: state.yearsKnown.size,
  });
  renderResults(resultsEl, hits);
}

let debounceId;
function debouncedSearch() {
  clearTimeout(debounceId);
  debounceId = setTimeout(triggerSearch, 200);
}

searchEl.addEventListener("input", debouncedSearch);
sortEl.addEventListener("change", triggerSearch);
document.querySelectorAll("#quick-keywords button").forEach(btn => {
  btn.addEventListener("click", () => {
    searchEl.value = btn.dataset.q;
    triggerSearch();
    searchEl.focus();
  });
});
document.querySelectorAll("input[name=conf]").forEach(i => i.addEventListener("change", triggerSearch));

loadShards();
