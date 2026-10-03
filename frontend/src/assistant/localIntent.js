const PHONE_10 = /(?<!\d)([6-9]\d{9})(?!\d)/g;

function cleanName(value) {
  const text = String(value || '').replace(/\s+/g, ' ').trim();
  if (!text || /^(null|none|n\/a|-)$/i.test(text)) return '';
  if (/^\d{12}$/.test(text.replace(/\D/g, '') || 'x')) return '';
  return text;
}

function titleName(value) {
  return value
    .split(' ')
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(' ');
}

export function parseLocalIntent(message) {
  const text = String(message || '').trim();
  const lower = text.toLowerCase();
  const actions = [];

  const wantsRegister = /(?:create|register|add)\s+(?:a\s+|new\s+)?farmer|new\s+farmer/.test(lower);
  const wantsProcurement = /record\s+procurement|procurement/.test(lower);
  const wantsStock = /add\s+(?:new\s+)?stock/.test(lower);
  const wantsOrder = /new\s+order|create\s+order/.test(lower);
  const wantsInvoice = /create\s+invoice|new\s+invoice/.test(lower);

  if (wantsRegister) {
    actions.push({ type: 'navigate', path: '/farmers' });
    actions.push({ type: 'open', target: 'register-farmer' });
  } else if (wantsProcurement) {
    actions.push({ type: 'navigate', path: '/farmers' });
    actions.push({ type: 'open', target: 'record-procurement' });
  } else if (wantsStock) {
    actions.push({ type: 'navigate', path: '/inventory' });
    actions.push({ type: 'open', target: 'add-stock' });
  } else if (wantsOrder) {
    actions.push({ type: 'navigate', path: '/sales' });
    actions.push({ type: 'open', target: 'new-order' });
  } else if (wantsInvoice) {
    actions.push({ type: 'navigate', path: '/finance' });
    actions.push({ type: 'open', target: 'create-invoice' });
  } else if (/mill\s*-?\s*flow/.test(lower)) {
    actions.push({ type: 'navigate', path: '/mill-flow' });
  } else if (/\binventory\b|\bstock\b/.test(lower)) {
    actions.push({ type: 'navigate', path: '/inventory' });
  } else if (/\bfarmers?\b/.test(lower)) {
    actions.push({ type: 'navigate', path: '/farmers' });
  } else if (/\bdashboard\b/.test(lower)) {
    actions.push({ type: 'navigate', path: '/dashboard' });
  }

  const fields = {};
  let nameMatch = text.match(/\bname\s+([A-Za-z][A-Za-z. ]{1,60}?)(?=\s+(?:phone|village|district|state|father)\b|[.,;]|$)/i);
  if (!nameMatch) {
    nameMatch = text.match(/(?:create|register|add)\s+(?:a\s+|new\s+)?farmer(?:\s+named)?\s+([A-Za-z][A-Za-z. ]{1,60})$/i);
  }
  const fullName = titleName(cleanName(nameMatch?.[1]));
  if (fullName) fields.fullName = fullName;

  PHONE_10.lastIndex = 0;
  let phoneMatch = PHONE_10.exec(text);
  while (phoneMatch) {
    const start = phoneMatch.index;
    const end = start + phoneMatch[1].length;
    const before = text.slice(Math.max(0, start - 2), start);
    const after = text.slice(end, end + 2);
    if (!/\d/.test(before) && !/\d/.test(after)) {
      fields.phone = phoneMatch[1];
      break;
    }
    phoneMatch = PHONE_10.exec(text);
  }

  if (Object.keys(fields).length) {
    if (!actions.some((item) => item.target === 'register-farmer')) {
      actions.push({ type: 'navigate', path: '/farmers' });
      actions.push({ type: 'open', target: 'register-farmer' });
    }
    actions.push({ type: 'fill', target: 'register-farmer', fields });
  }

  const reply = fields.fullName
    ? `Opening Register New Farmer and filling ${fields.fullName}. Review the form and press Save.`
    : (actions.length
      ? 'Opening that mill screen.'
      : '');

  return { reply, actions, engine: 'local' };
}
