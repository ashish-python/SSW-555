"""
Author: Ashish, Julia, Aaron
class GedcomParse includes methods to parse GEDCOM files
"""
from collections import defaultdict
import prettytable
import datetime
import TimeUtils
import unittest
import os

class GedcomParse():
    def __init__(self):
        self.tags_mapped_to_levels = {"0":{"INDI", "FAM","NOTE", "TRLR", "HEAD"},
        "1":{"NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "HUSB", "WIFE", "CHIL", "MARR", "DIV"}, 
        "2":{"DATE"}}
        
        self.repository = dict()
        self.current_record = dict()
        self.us42_errors_list = list()
        self.us38_list = list()

    def parseFile(self, file_name):
        """
        This method parses the GEDCOM file
        - checks for valid levels, and tags
        - checks for right mapping of level to tag
        - checks if a tag is in the correct position
        """
        try:
            fp = open(file_name, "r")
        except FileNotFoundError:
            raise FileNotFoundError("Could not open the file. Try again")
        else:
            parsed_line = list()
            length = len(parsed_line)
            with fp:
                counter = 0
                for line in fp:
                    counter+=1
                    parsed_line = line.rstrip("\n").split(" ", maxsplit=2)
                    #Check if the line has one of the special tags 'INDI' or 'FAM'
                    if len(parsed_line) == 3 and parsed_line[0] == '0' and parsed_line[2] in ('INDI', 'FAM'):
                        level, args, tag = parsed_line
                        valid = 'Y'
                        #INDI or FAM tag found
                        self.current_record["root"] = tag
                        self.current_record["root_id"] = args
                        #If the tag (INDI or FAM) is in the repository and tag_id not in the repository, create a dictionary for [tag][args]. Example ["INDI"]["ID01"]
                        #this will have all the information for this tag and id
                        if tag in self.repository:
                            if args not in self.repository[tag]:
                                self.repository[tag][args] = dict()
                        else:
                            self.repository[tag] = dict()
                            self.repository[tag][args] = dict() 
                    elif len(parsed_line) >= 2:
                        level, tag, args = parsed_line[0], parsed_line[1], " ".join(parsed_line[2:])
                        valid = 'Y' if level in self.tags_mapped_to_levels and tag in self.tags_mapped_to_levels[level] and tag not in ('INDI', 'FAM') else 'N'
                        if valid == "N":
                            continue
                        else: #A valid tag other than 'INDI' or 'FAM'
                            #these tags signify that a new record is going to start so clear the current repository.
                            if tag in ["NOTE","TRLR","HEAD"]:
                                self.current_record.clear()
                                continue
                            else:
                                if tag in ["BIRT", "DEAT", "MARR", "DIV"]:
                                    self.current_record["level_one_tag"] = tag
                                    if tag not in self.repository[self.current_record["root"]][self.current_record["root_id"]]:
                                        self.repository[self.current_record["root"]][self.current_record["root_id"]][tag] = "NA"
                                                     
                                else:
                                    if level == "2" and tag == 'DATE':
                                        date = self.check_date_legitimate(args, counter, parsed_line)
                                        if not date:
                                            self.repository[self.current_record["root"]][self.current_record["root_id"]][self.current_record["level_one_tag"]] = 'NA'
                                            continue                   
                                        self.repository[self.current_record["root"]][self.current_record["root_id"]][self.current_record["level_one_tag"]] = date
                                    else:
                                        if tag in ["FAMC", "FAMS"]:
                                            if tag not in self.repository[self.current_record["root"]][self.current_record["root_id"]]:
                                                self.repository[self.current_record["root"]][self.current_record["root_id"]][tag] = set()
                                            self.repository[self.current_record["root"]][self.current_record["root_id"]][tag].add(args)
                                        else:
                                            if tag == "CHIL":
                                                if tag not in self.repository[self.current_record["root"]][self.current_record["root_id"]]:
                                                    self.repository[self.current_record["root"]][self.current_record["root_id"]][tag] = set()
                                                self.repository[self.current_record["root"]][self.current_record["root_id"]][tag].add(args)
                                            else:
                                                self.repository[self.current_record["root"]][self.current_record["root_id"]][tag] = args
                    else:
                        #We can handle invalid entries here if we want
                        continue
            fp.close()
            #print parsed results
  
    def printResults(self):
        #---------------Individuals table-------------#
        
        if "INDI" in self.repository:
            pt_individuals = prettytable.PrettyTable(field_names=['ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouse'])
            sorted_repository = sorted(self.repository["INDI"])
            print("\nIndividuals table:")
            for id in sorted_repository:
                individual = self.repository["INDI"][id]
                name = individual['NAME'] if 'NAME' in individual else 'NA'
                gender = individual['SEX'] if 'SEX' in individual else 'NA'            
                birthday_datetime = individual['BIRT'] if ('BIRT' in individual and individual['BIRT'] is not 'NA') else 'NA'
                birthday = datetime.datetime.strftime(birthday_datetime, "%Y-%m-%d") if birthday_datetime is not 'NA' else 'NA'
                age = datetime.date.today().year - birthday_datetime.year if birthday_datetime is not 'NA' else 'NA'
                death_datetime = individual['DEAT'] if ('DEAT' in individual and individual['DEAT'] is not 'NA') else 'NA'
                death = datetime.datetime.strftime(death_datetime, "%Y-%m-%d") if death_datetime is not 'NA' else 'NA'
                alive = True if ('DEAT' not in individual or individual['DEAT'] is 'NA') else False
                child = individual['FAMC'] if 'FAMC' in individual else 'NA'
                spouse = individual['FAMS'] if 'FAMS' in individual else 'NA'
                pt_individuals.add_row([id, name, gender, birthday, age, alive, death, child, spouse])
            print(pt_individuals)
        #------------Families table-----------------#
        if 'FAM' in self.repository:
            pt_families = prettytable.PrettyTable(field_names=['ID', 'Married', 'Divorced', 'Husband ID', 'Husband Name', 'Wife ID', 'Wife Name', 'Children'])
            sorted_repository = sorted(self.repository['FAM'])
            print("\nFamilies table:")
            for id in sorted_repository:
                family = self.repository['FAM'][id]
                married_datetime = family['MARR'] if ('MARR' in family and family['MARR'] is not 'NA') else 'NA'
                married = datetime.datetime.strftime(married_datetime, "%Y-%m-%d") if married_datetime is not 'NA' else 'NA'
                divorced_datetime = family['DIV'] if ('DIV' in family and family['DIV'] is not 'NA') else 'NA'
                divorced = datetime.datetime.strftime(divorced_datetime, "%Y-%m-%d") if divorced_datetime is not 'NA' else 'NA'
                husband_id = family['HUSB'] if 'HUSB' in family else 'NA'
                husband_name = self.repository['INDI'][husband_id]['NAME'] if (husband_id is not 'NA' and 'NAME' in self.repository['INDI'][husband_id]) else 'NA'
                wife_id = family['WIFE'] if 'WIFE' in family else 'NA'
                wife_name = self.repository['INDI'][wife_id]['NAME'] if (wife_id is not 'NA' and 'NAME' in self.repository['INDI'][wife_id]) else 'NA'
                children = family['CHIL'] if 'CHIL' in family else 'NA'
                pt_families.add_row([id, married, divorced, husband_id, husband_name, wife_id, wife_name, children])
            print(pt_families)
    
                          
    
    def check_date_legitimate(self, date_str, line_num, parsed_line):
            if TimeUtils.legitimate_date(date_str):
                return TimeUtils.legitimate_date(date_str)
            else:
                self.us42_errors_list.append([line_num, parsed_line])
                return False

    #----------US42-Illegitimate dates------------#
    def us_42(self):    
        if len(self.us42_errors_list) != 0:
            print("\n\nUS42 - Illegitimate dates: ")
            for item in self.us42_errors_list:
                print ("Illegitimate date on line {} : {}".format(item[0], item[1][2]))
        else:
            print("\n\nUS42 - No illegitimate dates")
        
    #-------US38-List upcoming birthdays----------#
    def us_38(self, today = None):
        for id in self.repository["INDI"]:
            individual = self.repository["INDI"][id]
            if "BIRT" in individual  and individual["BIRT"] is not 'NA':
                birthday_date_month = individual["BIRT"].strftime("%d %b").upper()
                birthday_current_year = datetime.datetime.strptime(birthday_date_month + " " + str(datetime.date.today().year), "%d %b %Y")
                birthday_date = birthday_current_year.date()
                if today is None:
                    today = datetime.date.today()
                days_timedelta = birthday_date - today
                if days_timedelta.days >=0 and days_timedelta.days <=30:
                    self.us38_list.append([days_timedelta.days, id, individual['NAME'], birthday_date_month])
           
if __name__ == "__main__":   
    parser = GedcomParse()
    loop = True
    while loop:
        file_name = input("Please enter the name of GEDCOM file to parse: ")
        try:
            parser.parseFile(file_name)
            #prints individual and families tables
            parser.printResults()

            #------US42----------#
            #prints illegitimate dates list with line number
            parser.us_42()

            #-------US38---------#
            #This creates a list birthdays within the next 30 days
            parser.us_38()
            #This prints the birthday list
            if len(parser.us38_list) != 0:
                print("\nUS38 - Birthday's in the next 30 days")
                for item in parser.us38_list:
                    if item[2] == 'NA':
                        print("id: {}, Birthday: {}".format(item[1],item[3]))
                    else:
                        print("Name: {}, Birthday {}".format(item[2], item[3]))
            else:
                print("\nUS38 - No Birthday's in the next 30 days")
        except FileNotFoundError as e:
            print(e)
        else:
            loop = False

