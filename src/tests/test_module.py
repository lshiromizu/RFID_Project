import unittest
import module

class test(unittest.TestCase):
    
    def test_calculate_crc(self):
        data = bytes(b'\xA5\x5A\x0D\x0A')
        expected_crc = b'\xF8'
        result = module.calculate_crc(data)
        self.assertEqual(result, expected_crc)


if __name__ == '__main__':
    unittest.main()
