"""xAI Grok chat/vision client (OpenAI-compatible).

Does not load on Flask import of the app factory beyond this module.
Never logs the API key or Authorization header.
"""

import base64
import json
import logging
import os
import re
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

XAI_CHAT_URL = 'https://api.x.ai/v1/chat/completions'
DEFAULT_TEXT_MODEL = 'grok-2-latest'
DEFAULT_VISION_MODEL = 'grok-2-vision-1212'
VISION_FALLBACK_MODEL = 'grok-2-vision-latest'
TIMEOUT_SECONDS = 30

_AADHAAR = re.compile(r'(?<!\d)\d{12}(?!\d)')
_JSON_FENCE = re.compile(r'```(?:json)?\s*(\{.*?\})\s*```', re.S)


class GrokConfigError(RuntimeError):
    """Raised when XAI_API_KEY / GROK_API_KEY is missing."""


class GrokAPIError(RuntimeError):
    """Raised when the xAI HTTP API fails. Message never includes the key."""


def _load_dotenv_once():
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(backend_dir, '.env')
    if not os.path.isfile(path):
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(path, override=False)
    except ImportError:
        return


_load_dotenv_once()


def _api_key():
    return (os.environ.get('XAI_API_KEY') or os.environ.get('GROK_API_KEY') or '').strip()


def has_grok_key():
    return bool(_api_key())


def require_api_key():
    key = _api_key()
    if not key:
        raise GrokConfigError('XAI_API_KEY is not set')
    return key


def configured_model():
    return (os.environ.get('XAI_MODEL') or DEFAULT_TEXT_MODEL).strip() or DEFAULT_TEXT_MODEL


def _redact(text, key):
    value = text or ''
    if key and key in value:
        value = value.replace(key, '[redacted]')
    return value


def _error_message(raw, status, key):
    parsed = None
    try:
        parsed = json.loads(raw or '')
    except (TypeError, ValueError):
        parsed = None
    message = ''
    if isinstance(parsed, dict):
        err = parsed.get('error')
        if isinstance(err, dict):
            message = str(err.get('message') or err.get('code') or '')
        elif isinstance(err, str):
            message = err
        else:
            message = str(parsed.get('message') or '')
    if not message:
        message = (raw or '').strip() or f'xAI HTTP {status}'
    return _redact(message, key)[:500]


def _is_model_not_found(status, message):
    text = (message or '').lower()
    if status in (404, 400, 422) and 'model' in text:
        return any(token in text for token in (
            'not found', 'does not exist', 'unknown', 'invalid model', 'not available',
        ))
    return False


def _request(payload):
    key = require_api_key()
    body = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        XAI_CHAT_URL,
        data=body,
        method='POST',
        headers={
            'Authorization': 'Bearer ' + key,
            'Content-Type': 'application/json',
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode('utf-8', errors='replace')
        message = _error_message(raw, exc.code, key)
        raise GrokAPIError(message) from None
    except urllib.error.URLError as exc:
        reason = _redact(getattr(exc, 'reason', None) and str(exc.reason) or str(exc), key)
        raise GrokAPIError('xAI request failed: %s' % reason) from None
    except TimeoutError:
        raise GrokAPIError('xAI request timed out') from None

    try:
        data = json.loads(raw)
    except ValueError:
        raise GrokAPIError('xAI returned a non-JSON body') from None
    if not isinstance(data, dict):
        raise GrokAPIError('xAI returned an unexpected payload')
    return data


def _message_text(data):
    choices = data.get('choices') or []
    if not choices or not isinstance(choices[0], dict):
        return ''
    message = choices[0].get('message') or {}
    content = message.get('content')
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'text':
                parts.append(item.get('text') or '')
            elif isinstance(item, str):
                parts.append(item)
        return '\n'.join(parts).strip()
    return (content or '').strip()


def _unique(models):
    seen = set()
    ordered = []
    for model in models:
        name = (model or '').strip()
        if not name or name in seen:
            continue
        seen.add(name)
        ordered.append(name)
    return ordered


def _text_models():
    return _unique([configured_model(), DEFAULT_TEXT_MODEL])


def _vision_models():
    configured = configured_model()
    if 'vision' in configured.lower():
        return _unique([configured, DEFAULT_VISION_MODEL, VISION_FALLBACK_MODEL])
    return _unique([DEFAULT_VISION_MODEL, VISION_FALLBACK_MODEL, configured])


def _chat_with_models(messages, models):
    last_error = None
    for index, model in enumerate(models):
        try:
            data = _request({
                'model': model,
                'messages': messages,
                'temperature': 0.1,
            })
            return _message_text(data)
        except GrokAPIError as exc:
            last_error = exc
            if index + 1 < len(models) and _is_model_not_found(0, str(exc)):
                logger.info('grok_model_unavailable')
                continue
            raise
    raise last_error or GrokAPIError('xAI request failed')


def grok_chat(messages):
    """Send chat messages. Returns assistant text. Raises if no key or API fails."""
    if not messages:
        raise GrokAPIError('messages are required')
    return _chat_with_models(messages, _text_models())


def grok_vision(image_bytes, mime, prompt):
    """Send one image plus a text prompt. Returns assistant text."""
    require_api_key()
    if not image_bytes:
        raise GrokAPIError('image is required')
    media = (mime or 'image/jpeg').split(';')[0].strip().lower()
    if media == 'image/jpg':
        media = 'image/jpeg'
    if media not in ('image/jpeg', 'image/png', 'image/webp'):
        media = 'image/jpeg'
    encoded = base64.b64encode(image_bytes).decode('ascii')
    messages = [{
        'role': 'user',
        'content': [
            {
                'type': 'image_url',
                'image_url': {'url': 'data:%s;base64,%s' % (media, encoded)},
            },
            {'type': 'text', 'text': prompt or 'Describe this image briefly.'},
        ],
    }]
    return _chat_with_models(messages, _vision_models())


def grok_ping():
    """Short live check. Returns the model reply text."""
    return grok_chat([
        {'role': 'user', 'content': 'Reply with the single word pong.'},
    ])


def _clean_text(value, limit=80):
    text = re.sub(r'\s+', ' ', str(value or '')).strip(' -:.,')
    if not text or text.lower() in ('null', 'none', 'n/a', '-'):
        return None
    return text[:limit]


def _safe_phone(value):
    """10-digit Indian mobile. Never use a 12-digit Aadhaar as phone."""
    digits = re.sub(r'\D', '', str(value or ''))
    if not digits:
        return None
    if len(digits) == 10 and digits[0] in '6789':
        return digits
    if digits.startswith('91') and len(digits) == 12:
        rest = digits[2:]
        if rest[0] in '6789':
            return rest
    if len(digits) == 11 and digits[0] == '0' and digits[1] in '6789':
        return digits[1:]
    return None


def _safe_land(value):
    if value in (None, '', 'null', 'none'):
        return None
    try:
        acres = float(value)
    except (TypeError, ValueError):
        match = re.search(r'(\d+(?:\.\d+)?)', str(value))
        if not match:
            return None
        acres = float(match.group(1))
    if acres <= 0:
        return None
    return acres


def _extract_json_object(text):
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


def parse_grok_fields(text):
    """Map Grok JSON to farmer form keys. Never uses a 12-digit Aadhaar as phone."""
    data = _extract_json_object(text)
    if not data:
        return {}

    fields = {}
    name = _clean_text(data.get('fullName'))
    if name and not _AADHAAR.fullmatch(re.sub(r'\D', '', name) or 'x'):
        fields['fullName'] = name

    father = _clean_text(data.get('fatherName'))
    if father:
        fields['fatherName'] = father

    phone = _safe_phone(data.get('phone'))
    if phone:
        fields['phone'] = phone

    email = _clean_text(data.get('email'), 120)
    if email and '@' in email:
        fields['email'] = email

    for key in ('village', 'district', 'state'):
        value = _clean_text(data.get(key), 60)
        if value:
            fields[key] = value

    acres = _safe_land(data.get('landAcres'))
    if acres is not None:
        fields['totalLandArea'] = acres

    survey = _clean_text(data.get('surveyNumber'), 32)
    if survey:
        fields['surveyNumber'] = survey

    ifsc = _clean_text(data.get('ifsc') or data.get('bankIfsc'), 11)
    ifsc_ok = bool(ifsc and re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc.upper()))
    if ifsc_ok:
        fields['bankIfsc'] = ifsc.upper()

    account = re.sub(r'\D', '', str(data.get('bankAccount') or ''))
    if 9 <= len(account) <= 18:
        looks_like_mobile = len(account) == 10 and account[0] in '6789'
        looks_like_uid = len(account) == 12 and not ifsc_ok
        if not looks_like_mobile and not looks_like_uid:
            fields['bankAccount'] = account

    bank = _clean_text(data.get('bankName'), 60)
    if bank and 'ifsc' not in bank.lower():
        fields['bankName'] = bank

    return fields


ID_EXTRACT_PROMPT = (
    'Read this Indian farmer identity card or land passbook photo. '
    'Return JSON only with these keys: '
    'fullName, fatherName, phone, email, village, district, state, '
    'landAcres, surveyNumber, bankAccount, ifsc, bankName. '
    'phone must be a 10-digit Indian mobile starting with 6-9. '
    'Never use a 12-digit Aadhaar/UID as phone. '
    'Do not return an Aadhaar number in any field. '
    'Use an empty string when a value is not visible. '
    'landAcres is a number of acres when shown, else empty string. '
    'No markdown, no extra keys, no explanation.'
)
