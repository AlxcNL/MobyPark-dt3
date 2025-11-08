# test_calculator.py
import unittest
from v2.app.dependencies import calculate_price
from datetime import datetime, timedelta

class MockParkingLot:
    """Class voor parkinglot, omdat het nog niet bestaat"""
    def __init__(self, tariff, daytariff):
        self.tariff = tariff
        self.daytariff = daytariff

class TestCalculator(unittest.TestCase):
    def test_calculate_price(self):
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        test_parking_lot = MockParkingLot(20, 20)
        self.assertEqual(calculate_price(test_parking_lot, now, tomorrow), (20.0, 23, 1))

    def test_calulate_price_none_values(self):
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        test_parking_lot = MockParkingLot(None, None)
        self.assertEqual(calculate_price(test_parking_lot, now, tomorrow), (999.0, 23, 1))

    def test_negative_values(self):
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        test_parking_lot = MockParkingLot(20, -20)
        with self.assertRaises(ValueError):
            calculate_price(test_parking_lot, now, tomorrow)

if __name__ == "__main__":
    unittest.main()
