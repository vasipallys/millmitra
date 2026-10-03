"""MillMitra chat assistant: whitelist actions, Grok JSON, local fallback.

Never logs API keys, image bytes, or Aadhaar numbers.
Never invents quantities, phones, or names the user did not say.
"""

import json
import logging
import re

from services.access_control import has_permission
from services.grok_client import (
    GrokAPIError,
    GrokConfigError,
    _safe_phone,
    grok_chat,
    has_grok_key,
)

logger = logging.getLogger(__name__)

ALLOWED_NAVIGATE = (
    '/dashboard',
    '/mill-flow',
    '/farmers',
    '/inventory',
    '/production',
    '/sales',
    '/finance',
    '/customers',
    '/settings',
    '/users',
    '/lookups',
    '/access',
)

OPEN_PERMISSION = {
    'register-farmer': 'farmers',
    'add-stock': 'inventory',
    'record-procurement': 'farmers',
    'new-order': 'sales',
    'create-invoice': 'finance',
}

PATH_PERMISSION = {
    '/dashboard': 'dashboard',
    '/mill-flow': 'mill_flow',
    '/farmers': 'farmers',
    '/inventory': 'inventory',
    '/production': 'production',
    '/sales': 'sales',
    '/finance': 'finance',
    '/customers': 'customers',
    '/settings': 'settings',
    '/users': 'users',
    '/lookups': 'lookups',
    '/access': 'users',
}

FILL_KEYS = (
    'fullName',
    'fatherName',
    'phone',
    'email',
    'village',
    'district',
    'state',
    'variety',
    'product',
    'quantity',
    'price',
    'location',
)

FILL_TARGETS = (
    'register-farmer',
    'add-stock',
    'record-procurement',
)

_PHONE_10 = re.compile(r'(?<!\d)([6-9]\d{9})(?!\d)')
_TWELVE = re.compile(r'(?<!\d)\d{12}(?!\d)')
_JSON_FENCE = re.compile(r'```(?:json)?\s*(\{.*?\})\s*```', re.S)

SYSTEM_PROMPT = (
    'You are the MillMitra mill assistant. Reply with JSON only, no markdown. '
    'Shape: {"reply":"short helpful sentence","actions":[...]}. '
    'Allowed action types: '
    '{"type":"navigate","path":"<path>"}, '
    '{"type":"open","target":"<target>"}, '
    '{"type":"fill","target":"<target>","fields":{}}. '
    'Allowed paths: ' + ', '.join(ALLOWED_NAVIGATE) + '. '
    'Allowed open/fill targets: ' + ', '.join(OPEN_PERMISSION.keys()) + '. '
    'Fill field keys: ' + ', '.join(FILL_KEYS) + '. '
    'phone must be a 10-digit Indian mobile starting with 6-9. '
    'Never use a 12-digit number as phone. Never return an Aadhaar number. '
    'Never invent names, phones, prices, or quantities the user did not say. '
    'Do not submit forms. Tell the user to press Save after a fill. '
    'If the request is outside the mill screens, reply with help and empty actions.'
)


def _clean_name(value, limit=60):
    text = re.sub(r'\s+', ' ', str(value or '')).strip(' -:.,')
    if not text or text.lower() in ('null', 'none', 'n/a', '-'):
        return None
    if _TWELVE.fullmatch(re.sub(r'\D', '', text) or 'x'):
        return None
    return text[:limit]


def _clean_text(value, limit=80):
    text = re.sub(r'\s+', ' ', str(value or '')).strip()
    if not text or text.lower() in ('null', 'none', 'n/a', '-'):
        return None
    return text[:limit]


def _sanitize_fields(raw):
    if not isinstance(raw, dict):
        return {}
    fields = {}
    name = _clean_name(raw.get('fullName'))
    if name:
        fields['fullName'] = name
    father = _clean_name(raw.get('fatherName'))
    if father:
        fields['fatherName'] = father
    phone = _safe_phone(raw.get('phone'))
    if phone:
        fields['phone'] = phone
    email = _clean_text(raw.get('email'), 120)
    if email and '@' in email:
        fields['email'] = email
    for key in ('village', 'district', 'state', 'variety', 'product', 'location'):
        value = _clean_text(raw.get(key), 60)
        if value:
            fields[key] = value
    quantity = raw.get('quantity')
    if quantity not in (None, ''):
        try:
            number = float(quantity)
            if number > 0:
                fields['quantity'] = number
        except (TypeError, ValueError):
            match = re.search(r'(\d+(?:\.\d+)?)', str(quantity))
            if match and float(match.group(1)) > 0:
                fields['quantity'] = float(match.group(1))
    price = raw.get('price')
    if price not in (None, ''):
        try:
            number = float(price)
            if number > 0:
                fields['price'] = number
        except (TypeError, ValueError):
            match = re.search(r'(\d+(?:\.\d+)?)', str(price))
            if match and float(match.group(1)) > 0:
                fields['price'] = float(match.group(1))
    return fields


def _extract_json(text):
    raw = (text or '').strip()
    if not raw:
        return None
    fenced = _JSON_FENCE.search(raw)
    if fenced:
        raw = fenced.group(1)
    else:
        start = raw.find('{')
        end = raw.rfind('}')
        if start >= 0 and end > start:
            raw = raw[start:end + 1]
    try:
        data = json.loads(raw)
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def sanitize_actions(raw_actions):
    """Keep only whitelist navigate/open/fill. Drops unknown types."""
    actions = []
    if not isinstance(raw_actions, list):
        return actions
    for item in raw_actions:
        if not isinstance(item, dict):
            continue
        kind = str(item.get('type') or '').strip().lower()
        if kind == 'navigate':
            path = str(item.get('path') or '').strip()
            if path in ALLOWED_NAVIGATE:
                actions.append({'type': 'navigate', 'path': path})
        elif kind == 'open':
            target = str(item.get('target') or '').strip()
            if target in OPEN_PERMISSION:
                actions.append({'type': 'open', 'target': target})
        elif kind == 'fill':
            fields = _sanitize_fields(item.get('fields'))
            if not fields:
                continue
            target = str(item.get('target') or '').strip()
            action = {'type': 'fill', 'fields': fields}
            if target in FILL_TARGETS:
                action['target'] = target
            actions.append(action)
    return actions


def filter_actions(user, actions):
    """Drop actions the role cannot open. Returns (kept, denied_labels)."""
    kept = []
    denied = []
    for action in actions:
        kind = action.get('type')
        if kind == 'navigate':
            permission = PATH_PERMISSION.get(action['path'])
            if permission and not has_permission(user, permission):
                denied.append(action['path'])
                continue
        elif kind == 'open':
            permission = OPEN_PERMISSION.get(action['target'])
            if permission and not has_permission(user, permission):
                denied.append(action['target'])
                continue
        elif kind == 'fill':
            target = action.get('target')
            permission = OPEN_PERMISSION.get(target) if target else None
            if permission and not has_permission(user, permission):
                denied.append(target)
                continue
        kept.append(action)
    return kept, denied


def _reply_for_local(actions, language):
    lang = (language or 'en')[:2]
    if not actions:
        messages = {
            'en': (
                'I can open Farmers, Inventory, Mill flow, or Dashboard, '
                'register a farmer, or fill name and a 10-digit phone. '
                'Try: open farmers.'
            ),
            'hi': (
                'मैं किसान, इन्वेंटरी, मिल फ्लो या डैशबोर्ड खोल सकता हूँ, '
                'किसान पंजीकृत कर सकता हूँ, या नाम और 10 अंकों का फ़ोन भर सकता हूँ। '
                'कहें: open farmers.'
            ),
            'te': (
                'నేను రైతులు, ఇన్వెంటరీ, మిల్ ఫ్లో లేదా డాష్‌బోర్డ్ తెరవగలను, '
                'రైతును నమోదు చేయగలను, లేదా పేరు మరియు 10 అంకెల ఫోన్ నింపగలను. '
                'ఇలా చెప్పండి: open farmers.'
            ),
        }
        return messages.get(lang, messages['en'])

    kinds = {item['type'] for item in actions}
    if 'fill' in kinds:
        messages = {
            'en': 'I opened the form and filled the fields you said. Review them and press Save. I do not submit for you.',
            'hi': 'फ़ॉर्म खोलकर आपके बताए फ़ील्ड भर दिए। जाँचें और Save दबाएँ। मैं सबमिट नहीं करता।',
            'te': 'మీరు చెప్పిన ఫీల్డ్‌లు నింపాను. సరిచూసి Save నొక్కండి. నేను సమర్పించను.',
        }
        return messages.get(lang, messages['en'])
    if any(item.get('target') == 'register-farmer' for item in actions):
        messages = {
            'en': 'Opening Register New Farmer. You can speak a name and 10-digit phone, or attach an ID photo.',
            'hi': 'नया किसान पंजीकरण खोल रहा हूँ। नाम और 10 अंकों का फ़ोन बोलें, या आईडी फ़ोटो जोड़ें।',
            'te': 'కొత్త రైతు నమోదు తెరుస్తున్నాను. పేరు మరియు 10 అంకెల ఫోన్ చెప్పండి, లేదా ఐడీ ఫోటో జోడించండి.',
        }
        return messages.get(lang, messages['en'])
    messages = {
        'en': 'Opening that mill screen.',
        'hi': 'वह मिल स्क्रीन खोल रहा हूँ।',
        'te': 'ఆ మిల్ స్క్రీన్ తెరుస్తున్నాను.',
    }
    return messages.get(lang, messages['en'])


def parse_local_intent(message, route='', language='en'):
    """Small offline parser. Never invents data. 12-digit numbers are not phones."""
    text = (message or '').strip()
    lower = text.lower()
    actions = []

    wants_register = bool(re.search(
        r'(?:create|register|add)\s+(?:a\s+|new\s+)?farmer|new\s+farmer|किसान\s+पंजी|రైతును\s+నమోదు',
        lower,
    ))
    wants_procurement = bool(re.search(r'record\s+procurement|procurement', lower))
    wants_stock = bool(re.search(r'add\s+(new\s+)?stock', lower))
    wants_order = bool(re.search(r'new\s+order|create\s+order', lower))
    wants_invoice = bool(re.search(r'create\s+invoice|new\s+invoice', lower))

    if wants_register:
        actions.append({'type': 'navigate', 'path': '/farmers'})
        actions.append({'type': 'open', 'target': 'register-farmer'})
    elif wants_procurement:
        actions.append({'type': 'navigate', 'path': '/farmers'})
        actions.append({'type': 'open', 'target': 'record-procurement'})
    elif wants_stock:
        actions.append({'type': 'navigate', 'path': '/inventory'})
        actions.append({'type': 'open', 'target': 'add-stock'})
    elif wants_order:
        actions.append({'type': 'navigate', 'path': '/sales'})
        actions.append({'type': 'open', 'target': 'new-order'})
    elif wants_invoice:
        actions.append({'type': 'navigate', 'path': '/finance'})
        actions.append({'type': 'open', 'target': 'create-invoice'})
    elif re.search(r'mill\s*[- ]?flow', lower):
        actions.append({'type': 'navigate', 'path': '/mill-flow'})
    elif re.search(r'\binventory\b|\bstock\b', lower):
        actions.append({'type': 'navigate', 'path': '/inventory'})
    elif re.search(r'\bfarmers?\b', lower):
        actions.append({'type': 'navigate', 'path': '/farmers'})
    elif re.search(r'\bdashboard\b', lower):
        actions.append({'type': 'navigate', 'path': '/dashboard'})
    elif re.search(r'\bproduction\b', lower):
        actions.append({'type': 'navigate', 'path': '/production'})
    elif re.search(r'\bsales\b', lower):
        actions.append({'type': 'navigate', 'path': '/sales'})
    elif re.search(r'\bfinance\b', lower):
        actions.append({'type': 'navigate', 'path': '/finance'})
    elif re.search(r'\bcustomers?\b', lower):
        actions.append({'type': 'navigate', 'path': '/customers'})
    elif re.search(r'\bsettings\b', lower):
        actions.append({'type': 'navigate', 'path': '/settings'})

    fields = {}
    name_match = re.search(
        r'\bname\s+([A-Za-z][A-Za-z. ]{1,60}?)(?=\s+(?:phone|village|district|state|father)\b|[.,;]|$)',
        text,
        re.I,
    )
    if not name_match:
        name_match = re.search(
            r'(?:create|register|add)\s+(?:a\s+|new\s+)?farmer(?:\s+named)?\s+([A-Za-z][A-Za-z. ]{1,60})$',
            text,
            re.I,
        )
    if name_match:
        name = _clean_name(name_match.group(1))
        if name:
            fields['fullName'] = name.title()

    father_match = re.search(
        r'\bfather(?:\s+name)?\s+([A-Za-z][A-Za-z. ]{1,60}?)(?=\s+(?:phone|village|district|state|name)\b|[.,;]|$)',
        text,
        re.I,
    )
    if father_match:
        father = _clean_name(father_match.group(1))
        if father:
            fields['fatherName'] = father

    phone = None
    for match in _PHONE_10.finditer(text):
        start, end = match.span()
        before = text[max(0, start - 2):start]
        after = text[end:end + 2]
        if re.search(r'\d', before) or re.search(r'\d', after):
            continue
        phone = match.group(1)
        break
    if phone:
        fields['phone'] = phone

    village_match = re.search(r'\bvillage\s+([A-Za-z][A-Za-z. ]{1,40})', text, re.I)
    if village_match:
        village = _clean_text(village_match.group(1), 60)
        if village:
            fields['village'] = village

    if fields:
        if not any(item.get('target') == 'register-farmer' for item in actions):
            actions.append({'type': 'navigate', 'path': '/farmers'})
            actions.append({'type': 'open', 'target': 'register-farmer'})
        actions.append({'type': 'fill', 'target': 'register-farmer', 'fields': fields})

    qty_match = re.search(r'\bquantity\s+(\d+(?:\.\d+)?)', lower)
    price_match = re.search(r'\bprice\s+(\d+(?:\.\d+)?)', lower)
    stock_fields = {}
    if qty_match:
        stock_fields['quantity'] = float(qty_match.group(1))
    if price_match:
        stock_fields['price'] = float(price_match.group(1))
    if stock_fields and wants_stock:
        actions.append({'type': 'fill', 'target': 'add-stock', 'fields': stock_fields})
    elif stock_fields and wants_procurement:
        actions.append({'type': 'fill', 'target': 'record-procurement', 'fields': stock_fields})

    return {
        'reply': _reply_for_local(actions, language),
        'actions': sanitize_actions(actions),
        'engine': 'local',
    }


def _denied_text(denied, language):
    lang = (language or 'en')[:2]
    labels = ', '.join(denied)
    messages = {
        'en': ' Your role cannot open: %s.' % labels,
        'hi': ' आपकी भूमिका यह नहीं खोल सकती: %s।' % labels,
        'te': ' మీ రోల్ ఇవి తెరవదు: %s.' % labels,
    }
    return messages.get(lang, messages['en'])


def _grok_unavailable_text(language):
    lang = (language or 'en')[:2]
    messages = {
        'en': ' Grok is unavailable, so I used local commands only.',
        'hi': ' ग्रोक उपलब्ध नहीं है, इसलिए केवल स्थानीय कमांड चले।',
        'te': ' Grok అందుబాటులో లేదు, కాబట్టి స్థానిక కమాండ్‌లు మాత్రమే వాడాను.',
    }
    return messages.get(lang, messages['en'])


def grok_intent(message, route, language):
    content = grok_chat([
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {
            'role': 'user',
            'content': json.dumps({
                'message': message,
                'route': route or '',
                'language': language or 'en',
            }, ensure_ascii=False),
        },
    ])
    data = _extract_json(content)
    if not data:
        raise GrokAPIError('Grok returned non-JSON assistant output')
    reply = str(data.get('reply') or '').strip()
    actions = sanitize_actions(data.get('actions'))
    if not reply:
        reply = _reply_for_local(actions, language)
    return {'reply': reply, 'actions': actions, 'engine': 'grok'}


def run_assistant(message, route='', language='en', user=None):
    """Return {reply, actions, engine}. Falls back to local parser if Grok fails."""
    text = (message or '').strip()
    local = parse_local_intent(text, route, language)
    used_local_fallback = False
    payload = local

    if text and has_grok_key():
        try:
            payload = grok_intent(text, route, language)
        except (GrokConfigError, GrokAPIError):
            logger.info('assistant_grok_fallback')
            payload = local
            used_local_fallback = True
        except Exception:
            logger.exception('assistant_grok_failed')
            payload = local
            used_local_fallback = True

    actions, denied = filter_actions(user, payload.get('actions') or [])
    reply = str(payload.get('reply') or '').strip() or _reply_for_local(actions, language)
    if used_local_fallback:
        reply = (reply + _grok_unavailable_text(language)).strip()
    if denied:
        reply = (reply + _denied_text(denied, language)).strip()
    return {
        'reply': reply,
        'actions': actions,
        'engine': payload.get('engine') or 'local',
    }
