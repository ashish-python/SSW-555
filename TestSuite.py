import unittest
import TimeUtils
from Project import GedcomParse
import datetime

class TestSuite(unittest.TestCase):
    parser = GedcomParse()
    #User Story - 38
    #List upcoming birthdays
    #The file has birthdays that are today, in exactly 30 days, within the 30 day range, after 30 days, and birthday's that have passed
    def test_us38(self):
        self.parser.parseFile("US_38.txt")
        today_str = "18 SEP 2019"
        today = datetime.datetime.strptime(today_str, "%d %b %Y").date()
        self.parser.us_38(today)
        self.assertEqual(self.parser.us38_list,[[6, 'US38-I01', 'James /Cook/', '24 SEP'], [0, 'US38-I02', 'Jessica /Cook/', '18 SEP'], [30, 'US38-I05', 'Rita /Fuller/', '18 OCT']])
    
    #User Story - 42
    #Reject illegitimate dates
    def test_us42(self):
        self.assertEqual(TimeUtils.legitimate_date("30 FEB 2009"), False)
        self.assertEqual(TimeUtils.legitimate_date("0 JAN 2009"), False)
        self.assertEqual(TimeUtils.legitimate_date("DEC 2009"), False)
        self.assertEqual(TimeUtils.legitimate_date("MAR"), False)
        self.assertEqual(TimeUtils.legitimate_date("2019"), False)
        self.assertNotEqual(TimeUtils.legitimate_date("29 FEB 2020"), False) #Leap year


    #User Story - 01 
    #Finds any date that is after the current date
    def test_us01(self):
        self.parser.parseFile("US_01.txt")
        today_str = datetime.date.today()
        self.parser.us_01()
        self.assertEqual(self.parser.us01_list,[ 
        ['Birth', datetime.date(3140, 10, 21), 'I01', 'Leia /Skywalker/'], 
        ['Death', datetime.date(3490, 12, 27), 'I01', 'Leia /Skywalker/'], 
        ['Death', datetime.date(2022, 10, 21), 'I04', 'Padme /Amidala/'], 
        ['Divorce', datetime.date(2990, 4, 8), 'F01'], 
        ['Marriage', datetime.date(2980, 5, 9), 'F01']])

    #def test_us

if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)