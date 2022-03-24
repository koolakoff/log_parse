#!/usr/bin/env python3

# \file   parse_lib.py
# \author Peter Kulakov
# \date   2022 Mar 24
# \brief  engine of logs parser
#
#  to use the engine, just need register set of Parser objects
#  each object shoudl represent it's own event that we want to track from logs
#  then feed the logs lines to the Parser objects and it will return the result_line if match event or None if not
#
#  there are 2 use cases
#    - track one line log. In scope of this use case it is possible to register
#      -- regexp that would be chedked by logs parser engine automatically
#         Example:
#         parser_usb = Parser(r"usb.*Product:\ Mass\ Storage\ Device", result_line="USB detected")
#      -- or external function handler for parsing some specific cases
#          (i.e. when needs parse some info from log line)
#         Example:
#         def parse_hello(line):
#            if "hello" in line: return "a Hello event"
#         parser_usb = Parser(parse_hello)
#    - track multiple lines log. 
#      some cases may be tracked in log with few lines.
#      in this case it is possible to register the list of handlers (regex or external functions) 
#      for each of line. The parser will print result only when each of lines from the set is catched


import re
import types
import argparse

# \brief  the Parser class represetn parsing of specified event from the logs
#
class Parser(object):
   # \brief the Parser constructor
   # \param key - mandatory param, may be
   #                 - string   - the regex to parse (uses re.VERBOSE)
   #                 - function - the external function that woudl parse a line.
   #                 - list of strings or/and functions - when multiple line logs are traced
   # \param result_line - the optional parameter. The string to return if key detected in the log
   #                      Note, when 'key' is an external function then result_line is ignored and
   #                      result line is printed from the 'key' function return
   def __init__(self, key, result_line=True):
      self.result_line = result_line
      self.step = 0
      # check if 'key' has valid type - str for regex, function, or list for multiple lines handling
      if not isinstance(key, (str, types.FunctionType, list)):
         raise TypeError ("'key' argument has unsupported type {}".format(type(key)))
      # continue checking 'key' types - now if it is a list - check each elem of the list
      if isinstance(key, list):
         i = 0
         for elem in key:
            if not isinstance(elem, (str, types.FunctionType)):
               raise TypeError ("key[{}] argument has unsupported type {}".format(i,type(elem)))
            i += 1
      self.key     = key

   # \brief   check if a line contain the expected key
   # \param   line - the log line to check
   # \returns line if much single line or last line in sequence; None if not much or much intermediate elem of logs list
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
         

   # \brief  a buildt-in function for parsing a single regexp
   # \params key - the regexp to catch
   # \params line - the log line to check
   # \return None if regexp not found, or self.result_line if found
   def parse_single_regex(self, key, line):
      pattern = re.compile(key, re.VERBOSE)
      if pattern.search(line):
         return self.result_line
