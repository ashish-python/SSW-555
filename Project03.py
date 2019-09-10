"""
Author: 
class GedcomParse includes methods to parse GEDCOME files
"""
class GedcomParse():
    tags_mapped_to_levels = {"0":{"INDI", "FAM","NOTE", "TRLR", "HEAD"},
     "1":{"NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "HUSB", "WIFE", "CHIL", "MARR", "DIV"}, 
     "2":{"DATE"}}

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
                    print("--> " + line, end='')

                    if len(parsed_line) == 3 and parsed_line[0] == '0' and parsed_line[2] in ('INDI', 'FAM'):
                        level, args, tag = parsed_line
                        valid = 'Y'
                    elif len(parsed_line) >= 2:
                        level, tag, args = parsed_line[0], parsed_line[1], " ".join(parsed_line[2:])
                        valid = 'Y' if level in self.tags_mapped_to_levels and tag in self.tags_mapped_to_levels[level] and tag not in ('INDI', 'FAM') else 'N'
                    else:
                        level, tag, valid, args = parsed_line, 'NA', 'N', 'NA'
                    #print parsed results  
                    print(f"<-- {level}|{tag}|{valid}|{args}")
            fp.close()
    
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


    



