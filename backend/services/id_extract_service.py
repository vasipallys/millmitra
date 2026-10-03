"""Parse farmer ID / passbook text into existing registration fields.

Does not store images. Does not log image bytes or full Aadhaar numbers.
"""

import io
import logging
import os
import re

logger = logging.getLogger(__name__)

MAX_IMAGE_BYTES = 8 * 1024 * 1024
ALLOWED_TYPES = frozenset({'image/jpeg', 'image/jpg', 'image/png', 'image/webp'})
ALLOWED_SUFFIX = ('.jpg', '.jpeg', '.png', '.webp')

OCR_HELP = (
    'OCR is not installed on this mill PC. '
    'Run: pip install pytesseract pillow. '
    'Also install the Tesseract Windows binary '
    '(https://github.com/UB-Mannheim/tesseract/wiki) '
    'and add tesseract.exe to PATH.'
)

_AADHAAR_GROUPED = re.compile(r'(?<!\d)(\d{4}[\s-]?\d{4}[\s-]?\d{4})(?!\d)')
_AADHAAR_COMPACT = re.compile(r'(?<!\d)\d{12}(?!\d)')
_PHONE = re.compile(r'(?<!\d)([6-9]\d{9})(?!\d)')
_IFSC = re.compile(r'\b([A-Z]{4}0[A-Z0-9]{6})\b', re.I)
_EMAIL = re.compile(r'\b([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})\b', re.I)
_PIN = re.compile(r'(?<!\d)([1-9]\d{5})(?!\d)')
_LAND = re.compile(r'(\d+(?:\.\d+)?)\s*(?:acres?|ac\.?|hectare|hectares|ha\.?)\b', re.I)
_NAME_LINE = re.compile(
    r'(?:^|\n)\s*(?:name|naam|full\s*name)\s*[:\-]?\s*([A-Za-z][A-Za-z .]{1,60})',
    re.I,
)
_FATHER_LINE = re.compile(
    r'(?:father\'?s?\s*name|father|s\/o|c\/o|d\/o|w\/o)\s*[:\-]?\s*'
    r'([A-Za-z][A-Za-z .]{1,60})',
    re.I,
)
_VILLAGE = re.compile(
    r'(?:village|gram|gramam)\s*[:\-]?\s*([A-Za-z][A-Za-z .]{1,40})',
    re.I,
)
_DISTRICT = re.compile(
    r'(?:district|zilla)\s*[:\-]?\s*([A-Za-z][A-Za-z .]{1,40})',
    re.I,
)
_STATE = re.compile(
    r'(?:state|pradesh)\s*[:\-]?\s*([A-Za-z][A-Za-z .]{1,40})',
    re.I,
)
_ADDRESS = re.compile(r'(?:address|addr)\s*[:\-]?\s*(.+)', re.I)
_SURVEY = re.compile(
    r'(?:survey(?:\s*no\.?)?|sy\.?\s*no\.?|passbook(?:\s*(?:no\.?|number))?)\s*[:\-]?\s*'
    r'([A-Za-z0-9][A-Za-z0-9\/-]{0,24})',
    re.I,
)
_ACCOUNT = re.compile(
    r'(?:account(?:\s*no\.?)?|a\/c|bank\s*a(?:c|cc))\s*[:\-]?\s*([0-9]{9,18})',
    re.I,
)
_BANK_NAME = re.compile(
    r'(?:bank\s*name|bank)\s*[:\-]?\s*([A-Za-z][A-Za-z .]{2,40})',
    re.I,
)

_SKIP_NAME = frozenset({
    'government', 'india', 'unique', 'identification', 'authority',
    'aadhaar', 'aadhar', 'male', 'female', 'dob', 'year', 'address',
})


def _clean_name(value):
    text = re.sub(r'\s+', ' ', (value or '')).strip(' -:.,')
    if not text or len(text) < 2:
        return None
    first = text.split()[0].lower()
    if first in _SKIP_NAME:
        return None
    if not re.match(r'^[A-Za-z]', text):
        return None
    return text[:80]


def _aadhaar_digits(text):
    found = []
    for match in _AADHAAR_GROUPED.finditer(text or ''):
        digits = re.sub(r'\D', '', match.group(1))
        if len(digits) == 12:
            found.append(digits)
    for match in _AADHAAR_COMPACT.finditer(text or ''):
        digits = match.group(0)
        if digits not in found:
            found.append(digits)
    return found


def _strip_aadhaar(text):
    cleaned = _AADHAAR_GROUPED.sub(' ', text or '')
    return _AADHAAR_COMPACT.sub(' ', cleaned)


def parse_id_text(text):
    """Map OCR text to farmer form keys. Never uses a 12-digit Aadhaar as phone."""
    fields = {}
    raw = text or ''
    without_id = _strip_aadhaar(raw)

    name_match = _NAME_LINE.search(raw)
    name = _clean_name(name_match.group(1) if name_match else '')
    if name:
        fields['fullName'] = name

    father_match = _FATHER_LINE.search(raw)
    father = _clean_name(father_match.group(1) if father_match else '')
    if father:
        fields['fatherName'] = father

    aadhaars = set(_aadhaar_digits(raw))
    phones = [item for item in _PHONE.findall(without_id) if item not in aadhaars]
    if phones:
        fields['phone'] = phones[0]

    emails = _EMAIL.findall(raw)
    if emails:
        fields['email'] = emails[0]

    village = _VILLAGE.search(raw)
    if village:
        fields['village'] = village.group(1).strip(' -:.,')[:60]
    district = _DISTRICT.search(raw)
    if district:
        fields['district'] = district.group(1).strip(' -:.,')[:60]
    state = _STATE.search(raw)
    if state:
        fields['state'] = state.group(1).strip(' -:.,')[:60]

    address = _ADDRESS.search(raw)
    if address:
        line = re.sub(r'\s+', ' ', address.group(1)).strip()[:160]
        if line:
            fields['address'] = line

    pins = _PIN.findall(without_id)
    if pins:
        fields['pincode'] = pins[0]

    land = _LAND.search(raw)
    if land:
        try:
            acres = float(land.group(1))
            if acres > 0:
                fields['totalLandArea'] = acres
        except ValueError:
            pass

    survey = _SURVEY.search(raw)
    if survey:
        fields['surveyNumber'] = survey.group(1).strip()[:32]

    ifsc = _IFSC.search(raw)
    if ifsc:
        fields['bankIfsc'] = ifsc.group(1).upper()

    account = _ACCOUNT.search(without_id)
    if account:
        digits = account.group(1)
        if len(digits) != 12 and not (len(digits) == 10 and digits[0] in '6789'):
            fields['bankAccount'] = digits

    bank = _BANK_NAME.search(raw)
    if bank:
        label = bank.group(1).strip()
        if 'ifsc' not in label.lower() and 'account' not in label.lower():
            fields['bankName'] = label[:60]

    return fields


_TESSERACT_FALLBACKS = (
    os.environ.get('TESSERACT_CMD'),
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
)


def _configure_tesseract(pytesseract):
    """Use PATH first; otherwise the usual Windows install location."""
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        pass
    for candidate in _TESSERACT_FALLBACKS:
        if not candidate or not os.path.isfile(candidate):
            continue
        pytesseract.pytesseract.tesseract_cmd = candidate
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            continue
    return False


def _ocr_image(image_bytes):
    try:
        import pytesseract
        from PIL import Image
        if not _configure_tesseract(pytesseract):
            raise RuntimeError('tesseract binary not found')
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image) or ''
        return text, None
    except ImportError:
        pass
    except Exception:
        logger.info('id_extract_tesseract_failed')

    try:
        import easyocr
        import numpy as np
        from PIL import Image
        image = Image.open(io.BytesIO(image_bytes))
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        lines = reader.readtext(np.array(image), detail=0)
        return '\n'.join(str(line) for line in lines), None
    except ImportError:
        return None, OCR_HELP
    except Exception:
        logger.info('id_extract_easyocr_failed')
        return None, OCR_HELP


def _try_grok_extract(image_bytes, mime):
    """Use Grok vision when a key is set. Failures fall through to Tesseract."""
    try:
        from services.grok_client import (
            ID_EXTRACT_PROMPT,
            has_grok_key,
            grok_vision,
            parse_grok_fields,
        )
    except ImportError:
        return None
    if not has_grok_key():
        return None
    try:
        text = grok_vision(image_bytes, mime, ID_EXTRACT_PROMPT)
    except Exception:
        logger.info('id_extract_grok_failed')
        return None
    fields = parse_grok_fields(text)
    if not fields:
        return None
    return fields


def extract_id_document(image_bytes, filename='', mime=''):
    """OCR then parse. Missing OCR is a 200 with empty fields, not a startup error."""
    if not image_bytes:
        return {
            'success': True,
            'fields': {},
            'extracted': {},
            'notes': 'No image was received.',
            'engine': None,
        }
    if len(image_bytes) > MAX_IMAGE_BYTES:
        return {
            'success': False,
            'fields': {},
            'extracted': {},
            'notes': 'Image must be 8 MB or smaller.',
            'error': 'Image must be 8 MB or smaller.',
            'engine': None,
        }

    grok_fields = _try_grok_extract(image_bytes, mime)
    if grok_fields:
        return {
            'success': True,
            'fields': grok_fields,
            'extracted': grok_fields,
            'notes': (
                'Some details were filled from the document. '
                'Check them, then continue. The picture was not saved.'
            ),
            'engine': 'grok',
        }

    text, ocr_note = _ocr_image(image_bytes)
    if text is None:
        return {
            'success': True,
            'fields': {},
            'extracted': {},
            'notes': ocr_note or OCR_HELP,
            'engine': 'tesseract',
        }

    fields = parse_id_text(text)
    if not fields:
        notes = 'No details could be read from this image. Enter the fields by hand.'
    else:
        notes = (
            'Some details were filled from the document. '
            'Check them, then continue. The picture was not saved.'
        )
    return {
        'success': True,
        'fields': fields,
        'extracted': fields,
        'notes': notes,
        'engine': 'tesseract',
    }


def filename_allowed(filename, content_type=''):
    name = (filename or '').lower()
    ctype = (content_type or '').lower()
    if ctype in ALLOWED_TYPES:
        return True
    return name.endswith(ALLOWED_SUFFIX)
