chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.set({ enabled: true });
});

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('toggle');
  chrome.storage.sync.get('enabled', data => {
    toggle.checked = data.enabled;
  });
  toggle.addEventListener('change', () => {
    chrome.storage.sync.set({ enabled: toggle.checked });
  });
});