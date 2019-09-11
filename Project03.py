"""
Author: 
class GedcomParse includes methods to parse GEDCOME files
"""
from collections import defaultdict
import prettytable
import datetime

class GedcomParse():
    tags_mapped_to_levels = {"0":{"INDI", "FAM","NOTE", "TRLR", "HEAD"},
     "1":{"NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "HUSB", "WIFE", "CHIL", "MARR", "DIV"}, 
     "2":{"DATE"}}
    
    repository = dict()
    current_entry = dict()

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
                for line in fp:
                    parsed_line = line.rstrip("\n").split(" ", maxsplit=2)
                    #Check if the line has one of the special tags 'INDI' or 'FAM'
                    if len(parsed_line) == 3 and parsed_line[0] == '0' and parsed_line[2] in ('INDI', 'FAM'):
                        level, args, tag = parsed_line
                        valid = 'Y'
                        #INDI or FAM tag found
                        self.current_entry["root"] = tag
                        self.current_entry["root_id"] = args
                        #If the tag is in the repository and tag_id not in the repository, create a dictionary for [tag][args]. Example ["INDI"]["ID01"]
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
                            #these tags signify the close of previous related records
                            if tag in ["NOTE","TRLR","HEAD"]:
                                self.current_entry.clear()
                                continue
                            else:
                                if tag in ["BIRT", "DEAT", "MARR", "DIV"]:
                                    self.current_entry["level_one_tag"] = tag
                                    if tag not in self.repository[self.current_entry["root"]][self.current_entry["root_id"]]:
                                        self.repository[self.current_entry["root"]][self.current_entry["root_id"]][tag] = "NA"
                                                     
                                else:
                                    if level == "2":
                                        self.repository[self.current_entry["root"]][self.current_entry["root_id"]][self.current_entry["level_one_tag"]] = args
                                    else:
                                        if tag in ["FAMC", "FAMS"]:
                                            if tag not in self.repository[self.current_entry["root"]][self.current_entry["root_id"]]:
                                                self.repository[self.current_entry["root"]][self.current_entry["root_id"]][tag] = set()
                                            self.repository[self.current_entry["root"]][self.current_entry["root_id"]][tag].add(args)
                                        else:
                                            if tag == "CHIL":
                                                if tag not in self.repository[self.current_entry["root"]][self.current_entry["root_id"]]:
                                                    self.repository[self.current_entry["root"]][self.current_entry["root_id"]][tag] = set()
                                                self.repository[self.current_entry["root"]][self.current_entry["root_id"]][tag].add(args)
                                            else:
                                                self.repository[self.current_entry["root"]][self.current_entry["root_id"]][tag] = args
                                          
                    else:
                        #We can handle invalid entries here
                        continue
            fp.close()
            #print parsed results
            self.printResults()
    
    def printResults(self):
        pt_individuals = prettytable.PrettyTable(field_names=['ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouse'])
        sorted_repository = sorted(self.repository["INDI"])
        for id in sorted_repository:
            individual = self.repository["INDI"][id]
            name = individual['NAME'] if 'NAME' in individual else 'NA'
            gender = individual['SEX'] if 'SEX' in individual else 'NA'
            birthday = individual['BIRT'] if 'BIRT' in individual else 'NA'
            alive = True if 'DEAT' not in individual else False
            death = individual['DEAT'] if 'DEAT' in individual else 'NA'
            child = individual['FAMC'] if 'FAMC' in individual else 'NA'
            spouse = individual['FAMS'] if 'FAMS' in individual else 'NA'
            dt_birth = datetime.datetime.strptime(birthday, "%d %b %Y")
            dt_today = datetime.date.today()
            age = dt_today.year - dt_birth.year
            pt_individuals.add_row([id, name, gender, birthday, age, alive, death, child, spouse])
        print(pt_individuals)

        pt_families = prettytable.PrettyTable(field_names=['ID', 'Married', 'Divorced', 'Husband ID', 'Husband Name', 'Wife ID', 'Wife Name', 'Children'])
        sorted_repository = sorted(self.repository['FAM'])
        for id in sorted_repository:
            family = self.repository['FAM'][id]
            married = family['MARR'] if 'MARR' in family else 'NA'
            divorced = family['DIV'] if 'DIV' in family else 'NA'
            husband_id = family['HUSB'] if 'HUSB' in family else 'NA'
            husband_name = self.repository['INDI'][husband_id]['NAME'] if husband_id is not 'NA' else 'NA'
            wife_id = family['WIFE'] if 'WIFE' in family else 'NA'
            wife_name = self.repository['INDI'][wife_id]['NAME'] if wife_id is not 'NA' else 'NA'
            children = family['CHIL'] if 'CHIL' in family else 'NA'
            pt_families.add_row([id, married, divorced, husband_id, husband_name, wife_id, wife_name, children])
        print(pt_families)
            


if __name__ == "__main__":   
    parser = GedcomParse()
    loop = True
    while loop:
        file_name = input("Please enter the name of GEDCOM file to parse: ")
        try:
            parser.parseFile(file_name)
        except FileNotFoundError as e:
            print(e)
        else:
            loop = False


    



