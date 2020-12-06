# -*- coding: UTF-8 -*-
# @Author  : Jiachen <zhangjc1999 @ gmail.com>
# @Time    : 2020/9/21 18:15
import unittest
import narcissistic_number as narci

class TestNarcissisticNumber(unittest.TestCase):

    def test_case_1(self):
        pass

    def test_case_2(self):
        self.assertEqual([153], narci.find_narcissistic_number(100, 200))

    def test_case_3(self):
        self.assertEqual([], narci.find_narcissistic_number(100, 153))

    def test_case_4(self):
        self.assertEqual([153, 370, 371, 407], narci.find_narcissistic_number(100, 999))


if __name__ == '__main__':
    unittest.main()