"""tests demo with TDD"""

from django.test import SimpleTestCase

from app import calc

class CalcTests(SimpleTestCase):
    """ Test calc functions"""

    def test_add_method(self):
        """testing add method"""

        res = calc.add(4,56)

        self.assertEqual(res,60)
    
    def test_subtract_method(self):
        """testing subtract mthod"""

        res = calc.subtract(10,15)

        self.assertEqual(res, -5)