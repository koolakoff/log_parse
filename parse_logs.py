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
   def __init__(self, key, logline=True):
      self.logline = logline
      self.step = 0
      # check if 'key' has valid type - str for regex, function, or list for multiple lines handling
      if not isinstance(key, (str, types.FunctionType, list)):
         raise TypeError ("'key' argument has unsupported type {}".format(type(key)))
      if isinstance(key, list):
         i = 0
         for elem in key:
            if not isinstance(elem, (str, types.FunctionType)):
               raise TypeError ("key[{}] argument has unsupported type {}".format(i,type(elem)))
            i += 1
      self.key     = key

   # return line if much or None if not
   def parse(self, line):
      # first check if we work with sequence of log lines
      if isinstance(self.key, list):
         # we check sequence of lines so switch to handle corresponding element of sequence
         if self.step >= len(self.key): self.step = 0
         key = self.key[self.step]
      else:
         # we check one line log
         key = self.key
      # now actually execute log parse handler depending on key type
      #   for 'str' (regex) call internal handler
      #   for 'function' (external line parser) call this function
      if   isinstance(key, str):                result = self.parse_single_regex(key, line)
      elif isinstance(key, types.FunctionType): result = key(line)
      else:
         # suppose we never reach here as we checked types in constructor
         raise TypeError ("'key' argument of {} step has unsupported type".format(self.step))
      # handle result
      if isinstance(self.key, list):
         # we work with sequence of log lines, so increment line counter if current line parse success
         if result: self.step += 1
         # return result only if it is Last line in the logs sequence
         if self.step < len(self.key):
            result = None
      return result
         

   def parse_single_regex(self, key, line):
      pattern = re.compile(key, re.VERBOSE)
      if pattern.search(line):
         return self.logline



############## main body
# first check script's arguments
args_parser = argparse.ArgumentParser(description="parse kernel logs (dmesg) to find USB storage detection")
args_parser.add_argument("file", help="log filename")
args = args_parser.parse_args()

# config parser
def parse_devname(line):
   pattern = re.compile(r"(?P<time>\[\ *.*\])\ *sd[a-zA-Z]:\ (?P<devname>.*)", re.VERBOSE)
   match = pattern.search(line)
   if match: return "{} USB storage detected: {}".format(match.group("time"),match.group("devname"))

#parser_usb = Parser(r"usb.*Product:\ Mass\ Storage\ Device", logline="USB detected")
#parser_usb = Parser(parse_devname)
parser_usb = Parser([r"usb.*Product:\ Mass\ Storage\ Device",parse_devname])

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

