#!/usr/bin/env python3

# Log parser. It is a demo program

import re
import types
import argparse

# Brief: the Parser class - represents some specific event from the logs
#
#  there are 2 use cases
#    - track one line log. In scope of this use case it is possible to register
#      -- regexp that would be chedked by logs parser engine automatically
#      -- or function for parsing some specific cases (i.e. when needs parse some info from log line)
#    - track multiple lines log
#      in this case it is possible to register the state machine lookup engine
#      details usage <TDB>
#
#  it's methods
#    - __init__ - constructor takes at least 1 mandatory parameter. It may be
#                 - string   - the regex to parse (uses re.VERBOSE)
#                 - function - the external function that woudl parse a line.
#                              may be used when need parse some data from log line
#                 - list of strings or functions - when multiple line logs are traced
#    - Parse - check if log line carry current event
#
class Parser(object):
   def __init__(self, key, logline=None):
      self.key     = key
      self.logline = logline

   # return line if much or None if not
   def parse(self, line):
      if   isinstance(self.key, str):                return self.parse_single_regex(line)
      elif isinstance(self.key, types.FunctionType): return self.key(line)
      else:
         print ("unsupported key")
         return None

   def parse_single_regex(self, line):
      pattern = re.compile(self.key, re.VERBOSE)
      if pattern.search(line):
         return self.logline



############## main body
# first check script's arguments
args_parser = argparse.ArgumentParser(description="parse kernel logs (dmesg) to find USB storage detection")
args_parser.add_argument("file", help="log filename")
args = args_parser.parse_args()

# config parser
parser_usb = Parser(r"usb.*Product:\ Mass\ Storage\ Device", logline="USB stick detected")

# now go throught input file
# TODO support run with input stream, like 'dmesg|parse_logs.py'
filename = args.file
with open(filename, "r", encoding='utf-8', errors='ignore') as fp:
   line_num = 0
   for line in fp:
      line_num += 1
      res = parser_usb.parse(line)
      if res:
         print ("{} +{:<3} {}".format(filename, line_num, res))

