import unittest
import TimeUtils
from Project import GedcomParse
import datetime

class TestSuite(unittest.TestCase):

    #User Story - 38
    #List upcoming birthdays
    #The file has birthdays that are today, in exactly 30 days, within the 30 day range, after 30 days, and birthday's that have passed
    def test_us38(self):
        parser = GedcomParse()
        parser.parseFile("US_38.txt")
        today_str = "18 SEP 2019"
        today = datetime.datetime.strptime(today_str, "%d %b %Y").date()
        parser.us_38(today)
        self.assertEqual(parser.us38_list,[[6, 'US38-I01', 'James /Cook/', '24 SEP'], [0, 'US38-I02', 'Jessica /Cook/', '18 SEP'], [30, 'US38-I05', 'Rita /Fuller/', '18 OCT']])
    
    #User Story - 42
    #Reject illegitimate dates
    def test_us42(self):
        parser = GedcomParse()
        self.assertEqual(TimeUtils.legitimate_date("30 FEB 2009"), False)
        self.assertEqual(TimeUtils.legitimate_date("0 JAN 2009"), False)
        self.assertEqual(TimeUtils.legitimate_date("DEC 2009"), False)
        self.assertEqual(TimeUtils.legitimate_date("MAR"), False)
        self.assertEqual(TimeUtils.legitimate_date("2019"), False)
        self.assertNotEqual(TimeUtils.legitimate_date("29 FEB 2020"), False) #Leap year
    
    #User Story - 01 
    #Finds any date that is after the current date
    def test_us01(self):
        parser = GedcomParse()
        parser.parseFile("US_01.txt")
        today_str = "29 SEP 2019"
        today = datetime.datetime.strptime(today_str, "%d %b %Y").date()
        parser.us_01(today)
        self.assertEqual(parser.us01_list, [['Birth', datetime.date(2099, 7, 13), 'US01-I01', 'Han /Solo/'], ['Birth', datetime.date(3140, 10, 21), 'US01-I02', 'Leia /Skywalker/'], ['Death', datetime.date(3490, 12, 27), 'US01-I02', 'Leia /Skywalker/'], ['Death', datetime.date(2022, 10, 21), 'US01-I04', 'Padme /Amidala/'], ['Divorce', datetime.date(2990, 4, 8), 'US01-F01'], ['Marriage', datetime.date(2980, 5, 9), 'US01-F01']])

    #User Story - 22
    #Finds any repeated IDs 
    def test_us22(self):
        parser = GedcomParse()
        parser.parseFile("US_22.txt")
        self.assertEqual(parser.us22_list, [['INDI', 'US22-I01'], ['INDI', 'US22-I02'], ['FAM', 'US22-F01']])

    #User Story - 04
    #Marriage date before divorce date
    def test_us04(self):
        parser = GedcomParse()
        parser.parseFile("US_04.txt")
        parser.us_04()
        self.assertEqual(parser.us04_list,[['08 Jul 2010', '08 Jul 2020', 'F06']])

    #User Story - 05
    #Marriage date before death date
    def test_us05(self):
        parser = GedcomParse()
        parser.parseFile("US_05.txt")
        parser.us_05()
        self.assertEqual(parser.us05_list,[['F05', 'US05-I10', 'Randi /Gold/', '10 Oct 1985', '10 Jun 1984']])
    
    #User Story - 36
    #List recent deaths
    #The test file has deaths that are today, exactly 30 days ago, within the last 30 days, before the last 30 days, and date in the future
    def test_us36(self):
        parser = GedcomParse()
        parser.parseFile("US_36.txt")
        today_str = "02 OCT 2019"
        today = datetime.datetime.strptime(today_str, "%d %b %Y").date()
        parser.us_36(today)
        self.assertEqual(parser.us36_list,[[-7, 'US36-I01', 'James /Cook/', '25 Sep 2019'], [0, 'US36-I02', 'Jessica /Cook/', '02 Oct 2019'], [-30, 'US36-I05', 'Rita /Fuller/', '02 Sep 2019']])

    #User Story - 35
    #List recent births
    #The test file has births that are today, exactly 30 days ago, within the last 30 days, before the last 30 days, and a date in the future
    def test_us35(self):
        parser = GedcomParse()
        parser.parseFile("US_35.txt")
        today_str = "02 OCT 2019"
        today = datetime.datetime.strptime(today_str, "%d %b %Y").date()
        parser.us_35(today)
        self.assertEqual(parser.us35_list, [[-7, 'US35-I01', 'James /Cook/', '25 Sep 2019'], [0, 'US35-I02', 'Jessica /Cook/', '02 Oct 2019'], [-30, 'US35-I05', 'Rita /Fuller/', '02 Sep 2019']])
    
    #User Story - 08
    #Birth before marriage and/or 9 months after divorce
    def test_us08(self):
        parser = GedcomParse()
        parser.parseFile("US_08.txt")
        parser.us_08()
        self.assertEqual(parser.us08_list,[['Divorce', 'Benjamin /Solo/', 'US08-I5', '19 Nov 1991', '08 Apr 1990'], ['Marriage', 'Han /Solo/', 'US08-I1', '13 Jul 1942', '04 Aug 1950']])
    
    #User Story - 16
    #All male members of a family should have the same last name
    def test_us16(self):
        parser = GedcomParse()
        parser.parseFile("US_16.txt")
        parser.us_16()
        self.assertEqual(parser.us16_list,[['Benjamin /Ford/', 'Han /Solo/', 'US16-F1'], ['Jacen /Hamill/', 'Luke /Skywalker/', 'US16-F4']])

    #User Story - 06
    #Death before divorce
    def test_us06(self):
        parser = GedcomParse()
        parser.parseFile("US_06.txt")
        parser.us_06()
        self.assertEqual(parser.us06_list,[['F06', 'US06-I12', 'Jill /Maisel/', '08 Jul 1990', '05 Nov 1980']])

    #User Story - 07
    #Less than 150 years old
    def test_us07(self):
        parser = GedcomParse()
        parser.parseFile("US_07.txt")
        today_str = "09 OCT 2019"
        today = datetime.datetime.strptime(today_str, "%d %b %Y")
        parser.us_07(today)
        self.assertEqual(parser.us07_list, [['death_after_150', 'US07-I99', 'William /Burr/', '05 Jun 1850', '19 Dec 2001'], ['alive_over_150', 'US07-I01', 'Julia /Cahn/', '16 Sep 1800', '09 Oct 2019']])
    
    #User Story - 30
    #Living married people
    def test_us30(self):
        parser = GedcomParse()
        parser.parseFile("US_30.txt")
        parser.us_30()
        self.assertEqual(parser.us30_list,[['Husband', 'US30-F01', 'US30-I01', 'James /Cook/'], ['Wife', 'US30-F01', 'US30-I02', 'Jessica /Cook/']])


    #User Story - 31
    #Under 30 and never been married
    def test_us31(self):
        parser = GedcomParse()
        parser.parseFile("US_31.txt")
        today_str = "14 OCT 2019"
        today = datetime.datetime.strptime(today_str, "%d %b %Y").date()
        parser.us_31(today)
        self.assertEqual(parser.us31_list,[['US31-I03', 'Samantha /Hayes/', '09 May 1977', 42], ['US31-I05', 'Robbie /Williams/', '13 Oct 1989', 30]])

#User Story - 09
    #Birth before death of parents
    def test_us09(self):
        parser = GedcomParse()
        parser.parseFile("US_09.txt")
        today_str = "25 OCT 2019"
        today = datetime.datetime.strptime(today_str, "%d %b %Y").date()
        parser.us_09()
        self.assertEqual(parser.us09_list,[['US09-I11', 'US09-I09', '06 Feb 3000', '10 Jun 1900'], ['US09-I11', 'US09-I10', '06 Feb 3000', '10 Jun 1900']])

#User Story - 11
    #No Bigamy
    def test_us11(self):
        parser = GedcomParse()
        parser.parseFile("US_11.txt")
        today_str = "25 OCT 2019"
        today = datetime.datetime.strptime(today_str, "%d %b %Y").date()
        parser.us_11()
        self.assertEqual(parser.us31_list,[['US31-I03', 'Samantha /Hayes/', '09 May 1977', 42], ['US31-I05', 'Robbie /Williams/', '13 Oct 1989', 30]])

if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)