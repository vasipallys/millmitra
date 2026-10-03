"""Local assistant intent parser. No Grok calls, no image bytes."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.assistant_service import parse_local_intent, sanitize_actions


def _actions_of(result, kind):
    return [item for item in result.get('actions') or [] if item.get('type') == kind]


class AssistantParserTests(unittest.TestCase):
    def test_open_farmers(self):
        result = parse_local_intent('open farmers')
        paths = [item['path'] for item in _actions_of(result, 'navigate')]
        self.assertIn('/farmers', paths)
        self.assertTrue(result.get('reply'))

    def test_open_inventory(self):
        result = parse_local_intent('open inventory')
        paths = [item['path'] for item in _actions_of(result, 'navigate')]
        self.assertIn('/inventory', paths)

    def test_mill_flow_and_dashboard(self):
        mill = parse_local_intent('go to mill flow')
        dash = parse_local_intent('dashboard')
        self.assertIn('/mill-flow', [item['path'] for item in _actions_of(mill, 'navigate')])
        self.assertIn('/dashboard', [item['path'] for item in _actions_of(dash, 'navigate')])

    def test_register_farmer_opens_dialog(self):
        result = parse_local_intent('register farmer')
        targets = [item['target'] for item in _actions_of(result, 'open')]
        self.assertIn('register-farmer', targets)
        self.assertIn('/farmers', [item['path'] for item in _actions_of(result, 'navigate')])

    def test_create_new_farmer_siva(self):
        result = parse_local_intent('create new farmer siva')
        self.assertIn('/farmers', [item['path'] for item in _actions_of(result, 'navigate')])
        self.assertIn('register-farmer', [item['target'] for item in _actions_of(result, 'open')])
        fills = _actions_of(result, 'fill')
        self.assertTrue(fills)
        self.assertEqual(fills[0]['fields'].get('fullName'), 'Siva')
        self.assertNotIn('phone', fills[0]['fields'])
        self.assertEqual(fills[0].get('target'), 'register-farmer')

    def test_ten_digit_phone_fills_name(self):
        result = parse_local_intent('name Ramesh Kumar phone 9876543210')
        fills = _actions_of(result, 'fill')
        self.assertTrue(fills)
        fields = fills[0]['fields']
        self.assertEqual(fields.get('fullName'), 'Ramesh Kumar')
        self.assertEqual(fields.get('phone'), '9876543210')
        self.assertEqual(fills[0].get('target'), 'register-farmer')

    def test_twelve_digit_number_is_not_phone(self):
        result = parse_local_intent('name Ramesh phone 987654321012')
        fills = _actions_of(result, 'fill')
        phone = fills[0]['fields'].get('phone') if fills else None
        self.assertNotEqual(phone, '987654321012')
        self.assertTrue(not phone or len(str(phone)) == 10)
        if fills:
            self.assertEqual(fills[0]['fields'].get('fullName'), 'Ramesh')

    def test_sanitize_drops_unknown_path(self):
        kept = sanitize_actions([
            {'type': 'navigate', 'path': '/admin'},
            {'type': 'navigate', 'path': '/farmers'},
            {'type': 'open', 'target': 'delete-user'},
            {'type': 'fill', 'fields': {'phone': '123456789012', 'fullName': 'Ravi'}},
        ])
        self.assertEqual([item.get('path') for item in kept if item['type'] == 'navigate'], ['/farmers'])
        self.assertFalse(any(item.get('type') == 'open' for item in kept))
        fills = [item for item in kept if item['type'] == 'fill']
        self.assertEqual(fills[0]['fields'].get('fullName'), 'Ravi')
        self.assertNotIn('phone', fills[0]['fields'])


if __name__ == '__main__':
    unittest.main()
