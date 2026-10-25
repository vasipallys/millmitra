"""en / hi / te key sets must match. ur may omit keys that fall back to en."""

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
    'syncFailedCount', 'noDevices',
)


def _object_keys(source, name):
    match = re.search(r'const %s = \{([\s\S]*?)\n\};' % name, source)
    if not match:
        return set()
    return set(re.findall(r'^\s{2}([A-Za-z][A-Za-z0-9_]*)\s*:', match.group(1), re.M))


class I18nKeyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = open(TRANSLATIONS, encoding='utf-8').read()
        cls.en = _object_keys(cls.source, 'en')
        cls.hi = _object_keys(cls.source, 'hi')
        cls.te = _object_keys(cls.source, 'te')
        cls.ur = _object_keys(cls.source, 'ur')

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


if __name__ == '__main__':
    unittest.main()
