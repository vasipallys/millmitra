"""en / hi / te key sets must match. ur may omit keys that fall back to en.

hi/te values must be real translations except a small allowlist of brands,
codes, units, and language names that stay identical to English.
"""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TRANSLATIONS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'frontend', 'src', 'i18n', 'translations.js',
)

REQUIRED_NEW = (
    'iiot', 'formBuilder', 'dashboardBuilder', 'customFields', 'discrepancies',
    'syncNow', 'queuedCount', 'manualEntry', 'dynamicForms', 'perm_metadata',
    'perm_iiot', 'perm_reconciliation', 'labelEn', 'labelHi', 'labelTe',
    'farmerEntity', 'noFieldsYet', 'widgetProduction', 'recordSaved',
    'syncFailedCount', 'noDevices', 'comfortMode', 'commandPalette',
    'gettingStarted', 'navGroupDaily', 'pageHelp',
    'toastSuccess', 'orderId', 'noStockMovements', 'registerFirstFarmer',
    'fiSubtitle', 'gstPageSubtitle', 'notificationsTitle',
    'reorderAlerts', 'aiRecommendations', 'sampleInsights',
)

# Values that may equal English: tax codes, brands, units, language names.
ALLOW_SAME_VALUES = frozenset((
    'CGST', 'IGST', 'SGST', 'UPI', 'English', 'SQLite',
    'GST', 'IIoT', 'MQTT', 'CSV', 'API', 'OTP', 'PIN', 'HSN', 'kg',
    'MillMitra', 'GSTR-1', 'GSTR-2B', 'GSTR-3B', 'ID',
))


def _object_keys(source, name):
    match = re.search(r'const %s = \{([\s\S]*?)\n\};' % name, source)
    if not match:
        return set()
    return set(re.findall(r'^\s{2}([A-Za-z][A-Za-z0-9_]*)\s*:', match.group(1), re.M))


def _object_pairs(source, name):
    match = re.search(r'const %s = \{([\s\S]*?)\n\};' % name, source)
    if not match:
        return {}
    pairs = re.findall(
        r'^\s{2}([A-Za-z][A-Za-z0-9_]*)\s*:\s*"((?:\\.|[^"\\])*)"',
        match.group(1),
        re.M,
    )
    data = {}
    for key, value in pairs:
        data[key] = value
    return data


class I18nKeyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = open(TRANSLATIONS, encoding='utf-8').read()
        cls.en = _object_keys(cls.source, 'en')
        cls.hi = _object_keys(cls.source, 'hi')
        cls.te = _object_keys(cls.source, 'te')
        cls.ur = _object_keys(cls.source, 'ur')
        cls.en_pairs = _object_pairs(cls.source, 'en')
        cls.hi_pairs = _object_pairs(cls.source, 'hi')
        cls.te_pairs = _object_pairs(cls.source, 'te')

    def test_en_hi_te_match(self):
        self.assertTrue(self.en)
        missing_hi = sorted(self.en - self.hi)
        missing_te = sorted(self.en - self.te)
        self.assertEqual(missing_hi, [], 'hi missing %s' % missing_hi[:20])
        self.assertEqual(missing_te, [], 'te missing %s' % missing_te[:20])

    def test_new_chrome_keys_present(self):
        for key in REQUIRED_NEW:
            self.assertIn(key, self.en)
            self.assertIn(key, self.hi)
            self.assertIn(key, self.te)
            self.assertIn(key, self.ur, 'ur must ship real strings for new chrome (not only ...en)')

    def test_hi_te_not_english_copies(self):
        copies = []
        for key, english in self.en_pairs.items():
            if english.strip() in ALLOW_SAME_VALUES:
                continue
            for locale, pairs in (('hi', self.hi_pairs), ('te', self.te_pairs)):
                if key not in pairs:
                    continue
                if pairs[key] == english:
                    copies.append('%s.%s=%r' % (locale, key, english))
        self.assertEqual(copies, [], 'hi/te still copy English: %s' % copies[:20])


if __name__ == '__main__':
    unittest.main()
