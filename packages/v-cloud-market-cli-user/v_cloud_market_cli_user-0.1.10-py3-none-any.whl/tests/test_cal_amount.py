import unittest
from market_place_cli.service_interface_logic.common import calculate_amount

class TestCalAmount(unittest.TestCase):

    price_set = {'price': 100, 'chargingOptions': {'resourceUnit': '1-Unit-Resource'}, 'duration': {'100': 0.9, '200': 0.85, '0': 0.95 }}

    def test_50(self):
        result = calculate_amount(self.price_set, 50)
        self.assertEqual(result, 5000)

    def test_100(self):
        result = calculate_amount(self.price_set, 100)
        self.assertEqual(result, 9000)

    def test_150(self):
        
        result = calculate_amount(self.price_set, 150)
        self.assertEqual(result, 13500)

    def test_200(self):
        result = calculate_amount(self.price_set, 200)
        self.assertEqual(result, 17000)
