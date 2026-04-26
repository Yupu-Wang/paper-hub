const PAGE_SIZE = 50;
let currentHits = [];
let renderedCount = 0;
let observer;

export function renderResults(container, hits) {
  container.innerHTML = "";
  currentHits = hits;
  renderedCount = 0;
  if (hits === null) {
    container.innerHTML = '<p class="hint">输入关键词或选择筛选条件</p>';
    return;
  }
  if (hits.length === 0) {
    container.innerHTML = '<p class="hint">没有匹配结果</p>';
    return;
  }
  container.innerHTML = `<div class="summary-bar">共 ${hits.length} 条结果</div><ul id="paper-list"></ul><div id="sentinel" style="height:1px"></div>`;
  renderMore(container);
  attachInfiniteScroll(container);
}

function renderMore(container) {
  const list = container.querySelector("#paper-list");
  const slice = currentHits.slice(renderedCount, renderedCount + PAGE_SIZE);
  for (const p of slice) {
    list.appendChild(renderItem(p));
  }
  renderedCount += slice.length;
}

function renderItem(p) {
  const li = document.createElement("li");
  const tag = p.presentation ? ` · ${p.presentation}` : "";
  const abstract = p.abstract || "";
  const preview = abstract.slice(0, 200) + (abstract.length > 200 ? "…" : "");
  li.innerHTML = `
    <a href="${escapeAttr(p.url)}" target="_blank" rel="noopener">
      <div class="title">${escapeHtml(p.title)}</div>
      <div class="meta">${escapeHtml(p.conference)} ${p.year}${escapeHtml(tag)}</div>
      <div class="authors">${escapeHtml(p.authors.join(", "))}</div>
      <div class="abstract">${escapeHtml(preview)}</div>
    </a>
  `;
  return li;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

function escapeAttr(s) {
  return escapeHtml(s);
}

function attachInfiniteScroll(container) {
  if (observer) observer.disconnect();
  const sentinel = container.querySelector("#sentinel");
  if (!sentinel) return;
  observer = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting && renderedCount < currentHits.length) {
      renderMore(container);
    }
  });
  observer.observe(sentinel);
}
