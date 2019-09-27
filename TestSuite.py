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

     #User Story - 04
     #Marriage date before divorce date

    def test_us04(self):
        self.parser.parseFile("US_04.txt")
        self.parser.us_04()
        self.assertEqual(self.parser.us04_list,[
        [datetime.date(2010, 7, 8), datetime.date(2020, 7, 8), 'F06']
        ])

    #User Story - 05
    #Marriage date before death date
    def test_us05(self):
        self.parser.parseFile("US_05.txt")
        self.parser.us_05()
        self.assertEqual(self.parser.us05_list,[
        [datetime.date(1984, 6, 10), datetime.date(1985, 10, 10), 'US05-I10']])

if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)