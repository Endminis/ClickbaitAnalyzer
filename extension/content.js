const CARD = 'ytd-video-renderer,ytd-rich-item-renderer';
const TITLE_SEL = '#video-title';

let isEnabled = true;
chrome.storage.sync.get('enabled', data => {
  isEnabled = data.enabled;
});
chrome.storage.onChanged.addListener(changes => {
  if (changes.enabled) isEnabled = changes.enabled.newValue;
});

function scan(nodes) {
  if (!isEnabled) return;
  const batch = [];
  nodes.forEach(node => {
    const titleEl = node.querySelector(TITLE_SEL);
    if (titleEl) {
      const id = crypto.randomUUID();
      node.dataset.clickbaitId = id;
      batch.push({ id, text: titleEl.textContent.trim() });
    }
  });
  if (batch.length) chrome.runtime.sendMessage({ type: 'check', batch });
}

scan(document.querySelectorAll(CARD));
new MutationObserver(muts => muts.forEach(m =>
  scan([...m.addedNodes].filter(n => n.matches?.(CARD)))
)).observe(document, { childList: true, subtree: true });

chrome.runtime.onMessage.addListener(({ type, hits }) => {
  if (type === 'verdict' && isEnabled) {
    hits.forEach(id => {
      const el = document.querySelector(`[data-clickbait-id='${id}']`);
      if (el) el.style.display = 'none';
    });
  }
});