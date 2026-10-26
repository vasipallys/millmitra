const NOISE = /grammarly|message channel closed|react devtools|download the react devtools|chrome-extension:|moz-extension:|extension context invalidated/i;

export function isConsoleNoise(text) {
  return NOISE.test(String(text || ''));
}

export function attachConsoleGuard(page) {
  const failures = [];
  const onMessage = (msg) => {
    const text = msg.text();
    if (isConsoleNoise(text)) return;
    const type = msg.type();
    if (type === 'error') {
      failures.push(`error: ${text}`);
      return;
    }
    if (type === 'warning' && /validateDOMNesting|out-of-range|MUI: You have provided an out-of-range value/i.test(text)) {
      failures.push(`warning: ${text}`);
    }
  };
  const onPageError = (error) => {
    const text = String(error);
    if (!isConsoleNoise(text)) failures.push(`pageerror: ${text}`);
  };
  const notFound = [];
  const onResponse = (response) => {
    if (response.status() === 404) {
      notFound.push(response.url());
    }
  };
  page.on('console', onMessage);
  page.on('pageerror', onPageError);
  page.on('response', onResponse);
  return {
    failures,
    assertClean() {
      if (failures.length) {
        const extra = notFound.length ? `\n${notFound.map((url) => `404 ${url}`).join('\n')}` : '';
        throw new Error(`${failures.join('\n')}${extra}`);
      }
    },
  };
}
