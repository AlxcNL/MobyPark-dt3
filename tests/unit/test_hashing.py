import unittest
from app.dependencies import generate_payment_hash, tr_hash

class MockVehicle:
    def __init__(self, license_plate):
        self.license_plate = license_plate

class TestHashing(unittest.TestCase):
    def test_payment_hash(self) -> None:
        test_vehicle = MockVehicle(license_plate="AAA-AAA-222")
        self.assertEqual(generate_payment_hash("2", test_vehicle), "015b6229e1463bc8268b3ff9b542649c")

    def test_wrong_type(self) -> None:
        test_vehicle = MockVehicle(license_plate="AAA-AAA-222")
        test_vehicle_wrong_type = MockVehicle(license_plate=222)
        with self.assertRaises(TypeError):
            self.assertEqual(generate_payment_hash(2, test_vehicle), "015b6229e1463bc8268b3ff9b542649c")
            self.assertEqual(generate_payment_hash(2, test_vehicle_wrong_type), "015b6229e1463bc8268b3ff9b542649c")

    def test_tr_hash(self) -> None:
        test_vehicle = MockVehicle(license_plate="AAA-AAA-222")
        self.assertEqual(tr_hash(33, test_vehicle.license_plate), "87d87ec44347b39ca7b91d322517857f")

    def test_hr_hash_white_spaces(self):
        test_vehicle = MockVehicle(license_plate=" AAA-AAA-222 ")
        self.assertNotEqual(tr_hash(33, test_vehicle.license_plate), "87d87ec44347b39ca7b91d322517857f")

    def test_hr_negative_value(self):
        test_vehicle = MockVehicle(license_plate="AAA-AAA-222")
        self.assertIsNotNone(tr_hash(-33, test_vehicle.license_plate))
