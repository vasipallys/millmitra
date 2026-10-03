"""Parser-only tests. No image bytes, no OCR engine."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.id_extract_service import parse_id_text

AADHAAR_SAMPLE = """
GOVERNMENT OF INDIA
Name: RAMESH KUMAR
S/O SURESH KUMAR
1234 5678 9012
DOB: 01/01/1980
Mobile: 9876543210
Village: Nandipet
District: Nizamabad
State: Telangana
PIN: 503186
"""

AADHAAR_COMPACT = """
Name: ANITA REDDY
Father: VENKAT REDDY
987654321012
Address: House 9, Village Armoor
"""


class IdExtractParserTests(unittest.TestCase):
    def test_aadhaar_like_text_fills_name_not_uid_as_phone(self):
        fields = parse_id_text(AADHAAR_SAMPLE)
        self.assertEqual(fields.get('fullName'), 'RAMESH KUMAR')
        self.assertEqual(fields.get('fatherName'), 'SURESH KUMAR')
        self.assertEqual(fields.get('phone'), '9876543210')
        self.assertNotEqual(fields.get('phone'), '123456789012')
        self.assertNotIn('123456789012', str(fields.get('phone') or ''))
        self.assertEqual(fields.get('village'), 'Nandipet')
        self.assertEqual(fields.get('district'), 'Nizamabad')
        self.assertEqual(fields.get('state'), 'Telangana')

    def test_compact_twelve_digit_uid_is_not_phone(self):
        fields = parse_id_text(AADHAAR_COMPACT)
        self.assertEqual(fields.get('fullName'), 'ANITA REDDY')
        self.assertNotEqual(fields.get('phone'), '987654321012')
        self.assertTrue(not fields.get('phone') or len(fields.get('phone')) == 10)

    def test_bank_and_land_from_passbook_text(self):
        fields = parse_id_text(
            'Name: RAVI\nLand 2.5 acres\nSurvey No. 12/4\n'
            'Account No. 12345678901234\nIFSC SBIN0001234\nBank Name State Bank'
        )
        self.assertEqual(fields.get('fullName'), 'RAVI')
        self.assertEqual(fields.get('totalLandArea'), 2.5)
        self.assertEqual(fields.get('surveyNumber'), '12/4')
        self.assertEqual(fields.get('bankAccount'), '12345678901234')
        self.assertEqual(fields.get('bankIfsc'), 'SBIN0001234')


if __name__ == '__main__':
    unittest.main()
