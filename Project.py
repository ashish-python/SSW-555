"""
Author: Ashish, Julia, Aaron
class GedcomParse includes methods to parse GEDCOM files
"""
import prettytable
import datetime
import TimeUtils
import unittest
import os
from TimeUtils import datetime_to_string

class GedcomParse():
    def __init__(self):
        self.tags_mapped_to_levels = {"0":{"INDI", "FAM","NOTE", "TRLR", "HEAD"},
        "1":{"NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "HUSB", "WIFE", "CHIL", "MARR", "DIV"}, 
        "2":{"DATE"}}
        
        self.repository = dict()
        self.current_record = dict()
        self.us42_errors_list = list()
        self.us38_list = list()
        self.us01_list = list()
        self.us22_list = list()
        self.us04_list = list()
        self.us05_list = list()
        self.us36_list = list()
        self.us35_list = list()
        self.us08_list = list()
        self.us16_list = list()
        self.us06_list = list()
        self.us07_list = list()
        self.us30_list = list()
        self.us31_list = list()
        self.us09_list = list()
        self.us11_list = list()
        self.us23_list = list()
        self.us24_list = list()
        self.us15_list = list()
        self.us21_list = list()
    
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
                                self.us22_list.append([tag,args])
                                self.repository[tag][args].clear()
                                
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
                if "DEAT" in individual and individual["DEAT"] is not "NA":
                    alive = False
                elif ("BIRT" in individual and individual["BIRT"] is not "NA"):
                    alive = True
                else:
                    alive = "NA"
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
                husband_name = self.repository['INDI'][husband_id]['NAME'] if (husband_id is not 'NA' and husband_id in self.repository['INDI'] and 'NAME' in self.repository['INDI'][husband_id]) else 'NA'
                wife_id = family['WIFE'] if 'WIFE' in family else 'NA'
                wife_name = self.repository['INDI'][wife_id]['NAME'] if (wife_id is not 'NA' and wife_id in self.repository['INDI'] and 'NAME' in self.repository['INDI'][wife_id]) else 'NA'
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
                print ("ERROR: Illegitimate date on line {} : {}".format(item[0], item[1][2]))
        else:
            print("\n\nUS42 - No illegitimate dates")
        
    #-------US38-List upcoming birthdays----------#
    def us_38(self, today = None):
        if "INDI" in self.repository:
            if today is None:
                    today = datetime.date.today()
            for id in self.repository["INDI"]:
                individual = self.repository["INDI"][id]
                if "BIRT" in individual  and individual["BIRT"] is not 'NA' and individual["BIRT"].year < datetime.datetime.today().year:
                    birthday_date_month = individual["BIRT"].strftime("%d %b").upper()
                    birthday_current_year = datetime.datetime.strptime(birthday_date_month + " " + str(datetime.date.today().year), "%d %b %Y")
                    birthday_date = birthday_current_year.date()
                    days_timedelta = birthday_date - today
                    if days_timedelta.days >=0 and days_timedelta.days <=30:
                        name = individual['NAME'] if "NAME" in individual else "NA"
                        self.us38_list.append([days_timedelta.days, id, name, birthday_date_month])

    #-------------US01-Dates before current Date------------------#
    def us_01(self, today = None):
        if today is None:
            today = datetime.date.today()
        for id in self.repository['INDI']:
            individual = self.repository["INDI"][id]
            if "BIRT" in individual and individual['BIRT'] is not 'NA':
                date = individual['BIRT'].date()
                if (date > today):
                    self.us01_list.append(["Birth",date, id, individual['NAME']])

            if "DEAT" in individual and individual['DEAT'] is not 'NA':
                date = individual['DEAT'].date()
                if (date > today):
                    self.us01_list.append(["Death", date, id, individual['NAME']])
        if 'FAM' in self.repository:
            for id in self.repository['FAM']:
                family = self.repository["FAM"][id]
                if "DIV" in family and family['DIV'] is not 'NA':
                    date = family['DIV'].date()
                    if (date > today):
                        self.us01_list.append(["Divorce", date, id])

                    if "MARR" in family and family['MARR'] is not 'NA':
                        date = family['MARR'].date()
                        if (date > today):
                            self.us01_list.append(["Marriage",date, id])
          
    #------US04-Marriage before Divorce----------#
    def us_04(self):
        if 'FAM' in self.repository:
            for id in self.repository['FAM']:
                family = self.repository['FAM'][id]
                if "DIV" in family and family['DIV'] is not 'NA':
                    divorceDate = family['DIV'].date()
                    if 'MARR' in family and family['MARR'] is not 'NA' :
                        marriageDate = family['MARR'].date()
                        if (marriageDate > divorceDate):
                            self.us04_list.append([datetime.datetime.strftime(family["DIV"], "%d %b %Y"), datetime.datetime.strftime(family["MARR"], "%d %b %Y"), id])

    #----- US05-Death before Marriage ---------#
    def us_05(self):
        if 'FAM' in self.repository:
            for family_id in self.repository['FAM']:
                family = self.repository['FAM'][family_id]
                if "MARR" in family and family["MARR"] is not "NA":
                    if "HUSB" in family:
                        husband_id = family["HUSB"]
                        if husband_id in self.repository["INDI"] and "DEAT" in self.repository["INDI"][husband_id] and self.repository["INDI"][husband_id]["DEAT"] is not "NA":
                            if self.repository["INDI"][husband_id]["DEAT"] < family["MARR"]:
                                husband_name = self.repository["INDI"][husband_id]["NAME"] if "NAME" in self.repository["INDI"][husband_id] else "NA"
                                self.us05_list.append([family_id, husband_id, husband_name, datetime.datetime.strftime(family["MARR"], "%d %b %Y"), datetime.datetime.strftime(self.repository["INDI"][husband_id]["DEAT"], "%d %b %Y")])
                    if "WIFE" in family:
                        wife_id = family["WIFE"]
                        if wife_id in self.repository["INDI"] and "DEAT" in self.repository["INDI"][wife_id] and self.repository["INDI"][wife_id]["DEAT"] is not "NA":
                            if self.repository["INDI"][wife_id]["DEAT"] < family["MARR"]:
                                wife_name = self.repository["INDI"][wife_id]["NAME"] if "NAME" in self.repository["INDI"][wife_id] else "NA"
                                self.us05_list.append([family_id, wife_id, wife_name, datetime.datetime.strftime(family["MARR"], "%d %b %Y"), datetime.datetime.strftime(self.repository["INDI"][wife_id]["DEAT"], "%d %b %Y")])

    #-------US36-Recent deaths----------#
    def us_36(self, today = None):
        if today is None:
            today = datetime.date.today()
        if "INDI" in self.repository:
            for id in self.repository["INDI"]:
                individual = self.repository["INDI"][id]
                if "DEAT" in individual  and individual["DEAT"] is not 'NA' and individual["DEAT"].date() <= today:
                    death_datetime = individual['DEAT']
                    days_delta = death_datetime.date() - today
                    if days_delta.days <=0 and days_delta.days >= -30:
                        self.us36_list.append([days_delta.days, id, individual['NAME'], datetime.datetime.strftime(death_datetime, "%d %b %Y")])

    #-------US35-Recent births----------#
    def us_35(self, today = None):
        if today is None:
            today = datetime.date.today()
        if "INDI" in self.repository:
            for id in self.repository["INDI"]:
                individual = self.repository["INDI"][id]
                if "BIRT" in individual  and individual["BIRT"] is not 'NA' and individual["BIRT"].date() <= today:
                    birth_datetime = individual['BIRT']
                    days_delta = birth_datetime.date() - today
                    if days_delta.days <=0 and days_delta.days >= -30:
                        self.us35_list.append([days_delta.days, id, individual['NAME'], datetime.datetime.strftime(birth_datetime, "%d %b %Y")])
    
    #----- US08-Birth before Marriage ---------#
    def us_08(self):
        if "FAM" in self.repository:
            for family_id in self.repository['FAM']:
                family = self.repository['FAM'][family_id]
                if "CHIL" in family:
                    child_ids = family["CHIL"]
                    if "MARR" in family and family["MARR"] is not "NA":
                        marriageDate = family["MARR"].date()
                        for s in child_ids:
                            if s in self.repository['INDI'] and "BIRT" in self.repository['INDI'][s] and self.repository["INDI"][s]['BIRT'] is not 'NA':
                                childs_birthday = self.repository['INDI'][s]['BIRT'].date()
                                childs_name = self.repository['INDI'][s]['NAME']
                                if childs_birthday < marriageDate:
                                    self.us08_list.append(["Marriage", childs_name, s, datetime_to_string(childs_birthday), datetime_to_string(marriageDate)])
                    if "DIV" in family and family ["MARR"] is not "NA":
                        divorceDate = family["DIV"].date()
                        for s in child_ids:
                            if s in self.repository['INDI'] and "BIRT" in self.repository['INDI'][s] and self.repository["INDI"][s]['BIRT'] is not 'NA':
                                childs_birthday = self.repository['INDI'][s]['BIRT'].date()
                                childs_name = self.repository['INDI'][s]['NAME']
                                if childs_birthday > (divorceDate+datetime.timedelta(9*365/12)):
                                    self.us08_list.append(["Divorce", childs_name, s, datetime_to_string(childs_birthday), datetime_to_string(divorceDate)])
        
    #------ US16-Male Last Name -----------#
    def us_16(self):
        if "FAM" in self.repository:
            name = list()
            for family_id in self.repository['FAM']:
                family = self.repository['FAM'][family_id]
                if 'HUSB' in family:
                    husband_id = family["HUSB"]
                    if husband_id in self.repository["INDI"] :
                        name = self.repository['INDI'][husband_id]['NAME'].split('/')
                        husbandLastName = name[1]
                        if 'CHIL' in family:
                            child_id = family['CHIL']
                            for s in child_id:
                                if s in self.repository['INDI'] and self.repository['INDI'][s]['SEX'] is 'M':
                                    name = self.repository['INDI'][s]['NAME'].split('/')
                                    childLastName = name[1]
                                    if childLastName != husbandLastName:
                                        self.us16_list.append([self.repository['INDI'][s]['NAME'], self.repository['INDI'][husband_id]['NAME'], family_id]) 

    #--------US 06-Death before Divorce-------#
    def us_06(self):
        if "FAM" in self.repository:
            for family_id in self.repository['FAM']:
                family = self.repository['FAM'][family_id]
                if "DIV" in family and family["DIV"] is not "NA":
                    if "HUSB" in family:
                        husband_id = family["HUSB"]
                        if husband_id in self.repository["INDI"] and "DEAT" in self.repository["INDI"][husband_id] and self.repository["INDI"][husband_id]["DEAT"] is not "NA":
                            if self.repository["INDI"][husband_id]["DEAT"] < family["DIV"]:
                                husband_name = self.repository["INDI"][husband_id]["NAME"] if "NAME" in self.repository["INDI"][husband_id] else "NA"
                                self.us06_list.append([family_id, husband_id, husband_name, datetime_to_string(family["DIV"]), datetime_to_string(self.repository["INDI"][husband_id]["DEAT"])])
                    if "WIFE" in family:
                        wife_id = family["WIFE"]
                        if wife_id in self.repository["INDI"] and "DEAT" in self.repository["INDI"][wife_id] and self.repository["INDI"][wife_id]["DEAT"] is not "NA":
                            if self.repository["INDI"][wife_id]["DEAT"] < family["DIV"]:
                                wife_name = self.repository["INDI"][wife_id]["NAME"] if "NAME" in self.repository["INDI"][wife_id] else "NA"
                                self.us06_list.append([family_id, wife_id, wife_name, datetime_to_string(family["DIV"]), datetime_to_string(self.repository["INDI"][wife_id]["DEAT"])])
        
    #------------US07-Death should be less than 150 years after birth for dead people, and current date should be less than 150 years after birth for all living people--#
    def us_07(self, today = None):
        if "INDI" in self.repository:
            if today is None:
                today = datetime.datetime.today()
            for id in self.repository["INDI"]:
                individual = self.repository["INDI"][id]
                if "DEAT" in individual and individual["DEAT"] is not "NA" and "BIRT" in individual and individual["BIRT"] is not "NA" and individual["BIRT"] < today and individual["DEAT"] < today:
                    if individual["DEAT"] > individual["BIRT"] + datetime.timedelta(days = 365.25 * 150):
                        individual_name = individual["NAME"] if "NAME" in individual else "NA"
                        self.us07_list.append(["death_after_150", id, individual_name, datetime_to_string(individual["BIRT"]), datetime_to_string(individual["DEAT"])])

                if "BIRT" in individual and individual["BIRT"] is not "NA" and ("DEAT" not in individual or individual["DEAT"] is "NA") and individual['BIRT'] < today:
                    if individual["BIRT"] + datetime.timedelta(days = 365.25 * 150) < today:
                        individual_name = individual["NAME"] if "NAME" in individual else "NA"
                        self.us07_list.append(["alive_over_150", id, individual_name, datetime_to_string(individual["BIRT"]), datetime_to_string(today)])
    
    #-------US30-List all living married people----------#
    def us_30(self):
        if "INDI" in self.repository and "FAM" in self.repository:
            for family_id in self.repository["FAM"]:
                family = self.repository["FAM"][family_id]
                if "DIV" not in family or family["DIV"] is "NA":
                    if "HUSB" in family and family["HUSB"] in self.repository["INDI"] and ("DEAT" not in self.repository["INDI"][family["HUSB"]] or self.repository["INDI"][family["HUSB"]]["DEAT"] is "NA"):
                        if "WIFE" in family and family["WIFE"] in self.repository["INDI"] and ("DEAT" not in self.repository["INDI"][family["WIFE"]] or self.repository["INDI"][family["WIFE"]]["DEAT"] is "NA"):
                            husband_name = self.repository["INDI"][family["HUSB"]]["NAME"] if "NAME" in self.repository["INDI"][family["HUSB"]] else "NA"
                            self.us30_list.append(["Husband", family_id, family["HUSB"], husband_name])
                            wife_name = self.repository["INDI"][family["WIFE"]]["NAME"] if "NAME" in self.repository["INDI"][family["WIFE"]] else "NA"
                            self.us30_list.append(["Wife", family_id, family["WIFE"], wife_name])
                    
    #-------US31-Living people over 30 who have never been married----#
    def us_31(self, today = None):
        if "INDI" in self.repository:
            if today is None:
                today = datetime.date.today()
            for individual_id in self.repository["INDI"]:
                individual = self.repository["INDI"][individual_id]
                if "FAMS" not in individual and ("DEAT" not in individual or individual["DEAT"] is 'NA') and "BIRT" in individual and individual["BIRT"] is not "NA":
                    if individual["BIRT"].date() + datetime.timedelta(days = 365.25 * 30) < today:
                        individual_name = individual["NAME"] if "NAME" in individual else "NA"
                        self.us31_list.append([individual_id, individual_name, datetime_to_string(individual["BIRT"]), today.year - individual["BIRT"].year])
    
    #--------US 09-Birth before Death of parents-------#
    def us_09(self):
        if "FAM" in self.repository and "INDI" in self.repository:
            for family_id in self.repository['FAM']:
                family = self.repository['FAM'][family_id]
                if "CHIL" in family:
                    child_ids = family["CHIL"]
                    child_birthdays = dict()

                    for child_id in child_ids:
                        if child_id in self.repository["INDI"]:
                            if "BIRT" in self.repository["INDI"][child_id] and self.repository["INDI"][child_id] is not "NA":
                                child_birthdays[child_id] = self.repository["INDI"][child_id]["BIRT"]
                                
                    if "MARR" in family and family["MARR"] is not "NA":
                        if "HUSB" in family and family["HUSB"] is not "NA":
                            husband_id = family["HUSB"]
                            if "DEAT" in self.repository["INDI"][husband_id]:
                                husband_death_date = self.repository["INDI"][husband_id]["DEAT"]
                                for child_id in child_birthdays:
                                    if husband_death_date < child_birthdays[child_id]:
                                        self.us09_list.append([child_id, husband_id, datetime_to_string(child_birthdays[child_id]), datetime_to_string(husband_death_date)])

                        if "WIFE" in family and family["WIFE"] is not "NA":
                            wife_id = family["WIFE"]
                            if "DEAT" in self.repository["INDI"][wife_id]:
                                wife_death_date = self.repository["INDI"][wife_id]["DEAT"]
                                
                                for child_id in child_birthdays:
                                    if wife_death_date < child_birthdays[child_id]:
                                        self.us09_list.append([child_id, wife_id, datetime_to_string(child_birthdays[child_id]), datetime_to_string(wife_death_date)])
                       
    
    #--------US11-No bigamy---------------------------#
    def us_11(self):
        if "INDI" in self.repository and "FAM" in self.repository:
            for individual_id in self.repository['INDI']:
                individual = self.repository["INDI"][individual_id]
                if "FAMS" in individual and len(individual["FAMS"]) > 0:
                    s = individual["FAMS"]
                    l = sorted(list(s))
                    for i in range(len(individual["FAMS"])-1):
                        family_zero_id = l[0]
                        l.remove(family_zero_id)
                        if family_zero_id in self.repository["FAM"]:
                            for each_remaining_family_id in l:
                                if each_remaining_family_id in self.repository["FAM"]:
                                    #check if marriage date is available for both the families
                                    if "MARR" in self.repository["FAM"][each_remaining_family_id] and "MARR" in self.repository["FAM"][family_zero_id]:
                                        marriage_date_one = self.repository["FAM"][family_zero_id]["MARR"]
                                        marriage_date_two = self.repository["FAM"][each_remaining_family_id]["MARR"]
                                        individual_name = self.repository["INDI"][individual_id]["NAME"] if "NAME" in self.repository["INDI"][individual_id] else "NA"
                                        if marriage_date_one == marriage_date_two:
                                            self.us11_list.append(["same date marriage", individual_id, individual_name, family_zero_id, each_remaining_family_id, TimeUtils.datetime_to_string(marriage_date_one)])
                                            continue                                                      
                                        earlier_marriage_family_id = family_zero_id if self.repository["FAM"][family_zero_id]["MARR"] <  self.repository["FAM"][each_remaining_family_id]["MARR"] else each_remaining_family_id
                                        later_marriage_family_id = family_zero_id if self.repository["FAM"][family_zero_id]["MARR"] >  self.repository["FAM"][each_remaining_family_id]["MARR"] else each_remaining_family_id
                                        earlier_marriage_datetime = self.repository["FAM"][earlier_marriage_family_id]["MARR"]
                                        later_marriage_datetime = self.repository["FAM"][later_marriage_family_id]["MARR"]
                                        if "DIV" in self.repository["FAM"][earlier_marriage_family_id]:
                                            if later_marriage_datetime < self.repository["FAM"][earlier_marriage_family_id]["DIV"]:
                                                self.us11_list.append(["marriage before divorce", individual_id, individual_name, earlier_marriage_family_id, later_marriage_family_id, TimeUtils.datetime_to_string(earlier_marriage_datetime), TimeUtils.datetime_to_string(later_marriage_datetime), TimeUtils.datetime_to_string(self.repository["FAM"][earlier_marriage_family_id]["DIV"])])
                                        elif "HUSB" in self.repository["FAM"][earlier_marriage_family_id] and "WIFE" in self.repository["FAM"][earlier_marriage_family_id]:
                                            check_id_for_death = self.repository["FAM"][earlier_marriage_family_id]["WIFE"] if individual_id == self.repository["FAM"][earlier_marriage_family_id]["HUSB"] else self.repository["FAM"][earlier_marriage_family_id]["HUSB"]
                                            if check_id_for_death in self.repository["INDI"] and "DEAT" in self.repository["INDI"][check_id_for_death]:
                                                if later_marriage_datetime < self.repository["INDI"][check_id_for_death]["DEAT"]:
                                                    self.us11_list.append(["marriage before death", individual_id, individual_name, earlier_marriage_family_id, later_marriage_family_id, TimeUtils.datetime_to_string(earlier_marriage_datetime), TimeUtils.datetime_to_string(later_marriage_datetime), TimeUtils.datetime_to_string(self.repository["INDI"][check_id_for_death]["DEAT"])])

    #----------US23-Unique names---------------------------------#
    def us_23(self):
        final_list = list()
        if "INDI" in self.repository:
            for id in self.repository["INDI"]:
                individual = self.repository["INDI"][id]
                if individual["NAME"] not in final_list:
                    final_list.append(individual["NAME"])
                else : self.us23_list.append(["Name",individual["NAME"],id])
                if individual["BIRT"] not in final_list:
                    final_list.append(individual["BIRT"])
                else : self.us23_list.append(["Birthday",individual["NAME"],id, datetime_to_string(individual["BIRT"])])

    #------ US24-Unique spouses  ------------------------------#
    def us_24(self):
        final_list = list()
        check_list_dates = list()
        check_list_names = list()
        marriageDate = list()
        if "FAM" in self.repository:
                for family_id in self.repository['FAM']:
                    family = self.repository['FAM'][family_id]
                    if 'HUSB' in family:
                        husband_id = family['HUSB']
                        if husband_id in self.repository['INDI']:
                            husband_name = self.repository['INDI'][husband_id]["NAME"]
                    if 'WIFE' in family:
                        wife_id = family['WIFE']
                        if wife_id in self.repository['INDI']:
                            wife_name = self.repository['INDI'][wife_id]["NAME"]
                    if 'MARR' in family:
                        marriageDate = family["MARR"]
                    
                    final_list.append([marriageDate,wife_name,wife_id,family_id,husband_id,husband_name])
        i = 0
        j = i+1
        for i in range(len(final_list)):
            for j in range(i+1, len(final_list)):
                if final_list[i][0] == final_list[j][0]:
                    if final_list[i][1] == final_list[j][1]:
                        self.us24_list.append(["WIFE",datetime_to_string(final_list[i][0]), final_list[i][1], final_list[j][3], final_list[i][3]])
                if final_list [i][0] == final_list[j][0]:
                    if final_list[i][5] == final_list[j][5]:
                        self.us24_list.append(["HUSBAND", datetime_to_string(final_list[i][0]), final_list[i][5], final_list[j][3], final_list[i][3]])

     #-----US15-Fewer than 15 siblings-------------------------#
     #look at family
     #put children into a list
     #if the number of children in list is >16, add family ID to list
    def us_15(self):
        sibling_list = list()
        if "FAM" in self.repository:
                for family_id in self.repository['FAM']:
                    family = self.repository['FAM'][family_id]
                    if 'CHIL' in family:
                        child_id = family['CHIL']
                        if child_id in self.repository['INDI']:
                            child_list = self.repository['INDI'][child_id]
                            sibling_list.append([child_id])
                for i in range(len(sibling_list)):
                    if len(i) > 15 + 2:
                        self.us15_list.append([family_id])

   # def us_15(self):
    #    sibling_list = list ()
     #   if 'FAM' in self.repository:
      #      if 'CHIL' in self.repository:
       #         sibling_list.append([child_id])
        #if len(sibling_list) > 16:
         #   self.us15_list.append([family_id]}
                    

    #------US21-Correct role for sex-------------------------#
    def us_21(self):
        if "FAM" in self.repository:
            for family_id in self.repository['FAM']:
                family = self.repository['FAM'][family_id]
                if 'HUSB' in family:
                    husband_id = family["HUSB"]
                    for s in husband_id:
                        if s in self.repository['INDI'] and self.repository['INDI'][s]['SEX'] is not 'M':
                            self.us21_list.append([self.repository['INDI'][s]['NAME'], self.repository['INDI'][husband_id]['NAME'], family_id]) 
                if 'WIFE' in family:
                    wife_id = family["WIFE"]
                    for s in wife_id:
                        if s in self.repository['INDI'] and self.repository['INDI'][s]['SEX'] is not 'F':
                            self.us21_list.append([self.repository['INDI'][s]['NAME'], self.repository['INDI'][wife_id]['NAME'], family_id]) 

                                             
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
            print("\nUS38 - Birthday's in the next 30 days")
            #This prints the birthday list
            if len(parser.us38_list) != 0:
                for item in parser.us38_list:
                    if item[2] == 'NA':
                        print("id: {}, Birthday: {}".format(item[1], item[3]))
                    else:
                        print("Name: {}, id: {}, Birthday {}".format(item[2], item[1], item[3]))
            else:
                print("\nUS38 - No Birthday's in the next 30 days")
    
            #--------US01---------------#
            #Prints a list of birthdays, deaths, divorce, marriage dates that are after the current date
            parser.us_01()
            #This prints the dates after current date list
            if len(parser.us01_list) !=0:
                print("\nUS01 - Dates that are after the current date")
                for yoyo in parser.us01_list:
                    date_str = datetime.datetime.strftime(yoyo[1], "%d %b %Y")
                    if yoyo[0] == "Birth":
                        print("Name: {}, Birthdate: {}".format(yoyo[3], date_str))
                    if yoyo[0] == "Death":
                        print("Name: {}, Deathdate: {}".format(yoyo[3], date_str))
                    if yoyo[0] == "Marriage":
                        print("Family ID: {}, Marriage Date: {}".format(yoyo[2], date_str))
                    if yoyo[0] == "Divorce":
                        print("Family ID: {}, Divorce Date: {}".format(yoyo[2], date_str))
            else: print("\nUS01 - There are no current users with dates that are after the current date")
            
            #--------US22--------------#
            #This prints all of the IDs that are being repeated
            if len(parser.us22_list) !=0:
                print("\nUS22 - WARNING: The following IDs are being repeated")
                for i in parser.us22_list:
                    if i[0] == 'INDI':
                        print("Individual IDs {}".format(i[1]))
                    elif i[0] == 'FAM':
                        print("Family IDs {}".format(i[1]))
            else: print ("\nUS22 - All unique IDs")
                
            #----------Print results---US04-Marriage before divorce-----------#
            parser.us_04()
            if len(parser.us04_list) !=0:
                print("\nUS04- Marriage before Divorce")
                for marrdiv in parser.us04_list:
                    print("ERROR: Family ID: {}, Divorce date: {}, Marriage date: {}".format(marrdiv[2], marrdiv[0], marrdiv[1]))
            else: print("\nUS04-There are no divorce dates before marriage dates")
        
            #-------Print results---US05-Death before marriage----#
            parser.us_05()
            print("\nUS05 - Death before Marriage")
            if len(parser.us05_list) != 0:
                for item in parser.us05_list:
                    print("ERROR: Family ID: {}, individual_id: {}, Name: {}, Death: {}, Marriage: {}".format(item[0], item[1], item[2], item[3], item[4]))
            else:
                print("No Death before Marriage")

            #---------Print results---US36-List recent deaths----#
            parser.us_36()
            print("\nUS36 - Deaths in the last 30 days")
            if len(parser.us36_list) != 0:
                for item in parser.us36_list:
                    print("Name: {}, id: {}, Death date {}".format(item[2], item[1], item[3]))
            else:
                print("No Deaths in the last 30 days")

            #---------Print results---US35-List recent births----#
            parser.us_35()
            print("\nUS35 - Births in the last 30 days")
            if len(parser.us35_list) != 0:
                for item in parser.us35_list:
                    print("Name: {}, id: {}, Birth date {}".format(item[2], item[1], item[3]))
            else:
                print("No Births in the last 30 days")
            
            #------US08-Birth before marriage-------#
            # This will print out all of the births that are before marriage or any births that are after 9 months of a divorce 
            parser.us_08()
            if len(parser.us08_list) !=0:
                print ("\nUS08 - Birth after marriage or Birth after 9 months divorce")
                for item in parser.us08_list:
                    if (item[0] == "Marriage"):
                        print("ERROR: Child ID: {}, Child Name: {}, Child Birthday: {}, Parents Marriage Date: {}".format(item[2], item[1], item[3], item[4]))
                    if (item[0] == "Divorce"):
                        print("ERROR: Child ID: {}, Child Name: {}, Child Birthday: {}, Parents Divorce Date: {}".format(item[2], item[1], item[3], item[4]))
            else: 
                print("\nUS08 - There are no births after marriage or births after 9 months of divorce")

            #-------Print results---US06-Death before divorce----#
            parser.us_06()
            print("\nUS06 - Death before Divorce")
            if len(parser.us06_list) != 0:
                for item in parser.us06_list:
                    print("ERROR: Family ID: {}, Individual ID: {}, Name: {}, Death date: {}, Divorce date: {}".format(item[0], item[1], item[2], item[3], item[4]))
            else:
                print("No Death before Divorce")

            #-----Print results---US07---Age above 150----------#
            parser.us_07()
            print("\nUS07- Less than 150 years old")
            if len(parser.us07_list) != 0:
                for item in parser.us07_list:
                    if item[0] == "death_after_150":
                        print("ERROR: {} - Individual ID: {}, Name: {}, Birth date: {}, Death date: {}".format("Older than 150 at the time of death", item[1], item[2], item[3], item[4]))
                    else:
                        print("ERROR: {} - Individual ID: {}, Name: {}, Birth date: {}, Today's date: {}".format("Still alive and older than 150", item[1], item[2], item[3], item[4]))
            else:
                print("No one over 150 years old")

            #--------Print results---US30--List living married-----#
            parser.us_30()
            print("\nUS30 - List all living married people")
            if len(parser.us30_list) != 0:
                for item in parser.us30_list:
                    print("Family ID: {}, {}, Individual ID: {}, Name: {}".format(item[1], item[0] ,item[2], item[3]))
            else:
                print("No living married people")

            #--------Print results---US31--List all living people over 30 who have never been married-----#
            parser.us_31()
            print("\nUS31 - List all living people over 30 who have never been married")
            if len(parser.us31_list) != 0:
                for item in parser.us31_list:
                    print("Individual ID: {}, Name: {}, Birth date: {}".format(item[0], item[1] ,item[2]))
            else:
                print("No living people over 30 who have never been married")
           
 #------US16 - Male Last Name-------#
            # This will print out any males in the family that don't have the same last name
            parser.us_16()
            if len(parser.us16_list) !=0:
                print ("\nUS16 - Males without the same last name")
                for item in parser.us16_list:
                    print("ERROR: Family ID: {}, Child's Name: {}, Father's Name: {}".format(item[2], item[0], item[1]))
            else: 
                print("\nUS16 - All males in the family have the same last name")
            
            #-------Print results---US06-Death before divorce----#
            parser.us_06()
            print("\nUS06 - Death before Divorce")
            if len(parser.us06_list) != 0:
                for item in parser.us06_list:
                    print("ERROR: Family ID: {}, Individual ID: {}, Name: {}, Death date: {}, Divorce date: {}".format(item[0], item[1], item[2], item[3], item[4]))
            else:
                print("No Death before Divorce")

            #-----Print results---US07---Age above 150----------#
            parser.us_07()
            print("\nUS07- Less than 150 years old")
            if len(parser.us07_list) != 0:
                for item in parser.us07_list:
                    if item[0] == "death_after_150":
                        print("ERROR: {} - Individual ID: {}, Name: {}, Birth date: {}, Death date: {}".format("Older than 150 at the time of death", item[1], item[2], item[3], item[4]))
                    else:
                        print("ERROR: {} - Individual ID: {}, Name: {}, Birth date: {}, Today's date: {}".format("Still alive and older than 150", item[1], item[2], item[3], item[4]))
            else:
                print("No one over 150 years old")

            #--------Print results---US30--List living married-----#
            parser.us_30()
            print("\nUS30 - List all living married people")
            if len(parser.us30_list) != 0:
                for item in parser.us30_list:
                    print("Family ID: {}, {}, Individual ID: {}, Name: {}".format(item[1], item[0] ,item[2], item[3]))
            else:
                print("No living married people")

            #--------Print results---US31--List all living people over 30 who have never been married-----#
            parser.us_31()
            print("\nUS31 - List all living people over 30 who have never been married")
            if len(parser.us31_list) != 0:
                for item in parser.us31_list:
                    print("Individual ID: {}, Name: {}, Birth date: {}".format(item[0], item[1] ,item[2]))
            else:
                print("No living people over 30 who have never been married")

            #--------Print results---US09--Birth before death of parents-------------#
            parser.us_09()
            print("\nUS09 - Birth before death of parents")
            if len(parser.us09_list) != 0:
                for item in parser.us09_list:
                    print("Child ID: {}, Parent ID: {}, Child death date: {}, Parent death date: {}".format(item[0], item[1], item[2], item[3]))
            else:
                print("No births before death of parents")
            
            #--------Print results for US11--No Bigamy--------------------------#
            parser.us_11()
            print ("\nUS11 - No Bigamy - Marriage should not occur during marriage to another spouse")
            if len(parser.us11_list) != 0:
                for item in parser.us11_list:
                    if item[0] == "marriage before divorce":
                        print("ERROR: Second marriage before divorce - Individual ID: {}, Individual name: {}, Family ID-1: {}, Family ID-2: {}, First marriage date: {}, Second marriage date: {}, First marriage divorce date: {} ".format(item[1], item[2], item[3], item[4], item[5], item[6], item[7]))
                    elif item[0] == "marriage before death":
                        print("ERROR: Married again before death of spouse - Individual ID: {}, Individual name: {}, Family ID-1: {}, Family ID-2: {}, First marriage date: {}, Second marriage date: {}, Death of spouse in first marriage: {} ".format(item[1], item[2], item[3], item[4], item[5], item[6], item[7]))
                    elif item[0] == "same date marriage":
                        print("ERROR: Both marriages on the same date - Individual ID: {}, Individual name: {}, Family ID 1: {}, Family ID 2: {}, Marriage date: {}".format(item[1], item[2], item[3], item[4], item[5]))
                
            #-----Print results---US23---Unique birthdays and unique names----------#
            parser.us_23()
            print ("\nUS23 - Unique names and birthdays")
            if len(parser.us23_list ) !=0:
                for item in parser.us23_list:
                    if item[0] == "Name":
                        print("ERROR SAME NAME: ID: {}, Name: {}".format(item[2], item[1]))
                    if item[0] == "Birthday":
                        print("ERROR SAME BIRTHDAY: ID: {}, Name: {}, Birthday: {}".format(item[2],item[1],item[3]))
            else :    
                print("All names and birthdays are all unique")
            
            #-----Print results---US24---Unique spouses and marriage date----------#
            parser.us_24()
            print ("\nUS24 - Unique spouses and marriage dates")
            if len(parser.us24_list ) !=0:
                for item in parser.us24_list:
                    if item[0] == "HUSBAND":
                        print("ERROR SAME HUSBAND ON THE SAME MARRIAGE DATE: Family ID 1 : {}, Family ID 2: {}, Name: {}, Marriage date: {}".format(item[3], item[4], item[2], item[1]))
                    if item[0] == "WIFE":
                        print("ERROR SAME WIFE ON THE SAME MARRIAGE DATE: Family ID 1 : {}, Family ID 2: {}, Name: {}, Marriage date: {}".format(item[3], item[4], item[2], item[1]))
            else :    
                print("All spouses and marriage dates are unique")
                
            #-----Print results--US15----Fewer than 15 siblings------------------#
            parser.us_15()
            print ("\nUS15 - Fewer than 15 siblings")
            if len(parser.us15_list) !=0:
                for item in parser.us15_list:
                    print("ERROR FAMILY TOO LARGE: Family ID: {}".format(item[0]))
            else:
                print("All families are appropriately sized")

            #----Print results--US21----Correct role for sex---------------------#
            parser.us_21()
            print("\nUS21 - Correct role for sex")
            if len(parser.us21_list) != 0:
                for item in parser.us21_list:
                    print("Name: {}, Individual ID: {}, Family ID: {}".format(item[0], item[1], item[2]))
            else:
                print("All roles correspond with correct sex of individuals")
           
        except FileNotFoundError as e:
            print(e)
        else:
            loop = False

