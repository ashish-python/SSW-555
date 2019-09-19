import unittest
import os

class TestSuite(unittest.TestCase):
    #current directory
    dir = "."
    file_name = "us42.txt"
    path = os.path.join(dir,file_name)

      


if __name__=="__main__":
    unittest.main(verbosity=2,exit=False)