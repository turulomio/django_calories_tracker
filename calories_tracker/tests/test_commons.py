from django.test import TestCase
from calories_tracker import commons

class CommonsFunctionsTest(TestCase):

    def test_string2list_of_integers(self):
        # Test case 1: Standard comma-separated string
        s1 = "1, 2, 3, 4"
        expected1 = [1, 2, 3, 4]
        self.assertEqual(commons.string2list_of_integers(s1), expected1)

        # Test case 2: Empty string
        s2 = ""
        expected2 = []
        self.assertEqual(commons.string2list_of_integers(s2), expected2)

        # Test case 3: Single integer string
        s3 = "5"
        expected3 = [5]
        self.assertEqual(commons.string2list_of_integers(s3), expected3)

        # Test case 4: String with different separator
        s4 = "10;20;30"
        expected4 = [10, 20, 30]
        self.assertEqual(commons.string2list_of_integers(s4, separator=";"), expected4)

        # Test case 5: String with spaces around numbers
        s5 = " 1 ,  22 , 333 "
        expected5 = [1, 22, 333]
        self.assertEqual(commons.string2list_of_integers(s5), expected5)

        # Test case 6: Invalid input (non-integer string) - expect ValueError
        s6 = "1, 2, abc"
        with self.assertRaises(ValueError):
            commons.string2list_of_integers(s6)

    def test_list_of_integers2string(self):
        # Test case 1: Standard list of integers
        arr1 = [1, 2, 3, 4]
        expected1 = "1, 2, 3, 4"
        self.assertEqual(commons.list_of_integers2string(arr1), expected1)

        # Test case 2: Empty list
        arr2 = []
        expected2 = ""
        self.assertEqual(commons.list_of_integers2string(arr2), expected2)

        # Test case 3: Single integer list
        arr3 = [5]
        expected3 = "5"
        self.assertEqual(commons.list_of_integers2string(arr3), expected3)

        # Test case 4: List with different separator
        arr4 = [10, 20, 30]
        expected4 = "10; 20; 30"
        self.assertEqual(commons.list_of_integers2string(arr4, separator="; "), expected4)

        # Test case 5: List containing zero
        arr5 = [0, 1, 2]
        expected5 = "0, 1, 2"
        self.assertEqual(commons.list_of_integers2string(arr5), expected5)

        # Test case 6: List containing negative numbers
        arr6 = [-1, 0, 1]
        expected6 = "-1, 0, 1"
        self.assertEqual(commons.list_of_integers2string(arr6), expected6)
