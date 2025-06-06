chrome.runtime.onMessage.addListener(async (msg, sender) => {
  if (msg.type !== 'check') return;

  try {
    const res = await fetch('http://localhost:5000/extension/api/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(msg.batch.map(o => o.text))
    });
    const verdict = await res.json();

    const hits = msg.batch
      .filter((o, i) => verdict[i] === true)
      .map(o => o.id);

    chrome.tabs.sendMessage(sender.tab.id, { type: 'verdict', hits });
  } catch (err) {
    console.error('API error', err);
  }
});