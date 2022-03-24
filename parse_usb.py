#!/usr/bin/env python3

# \file   parse_usb.py
# \author Peter Kulakov
# \date   2022 Mar 24
# \brief  an example of logs parser usage
#
# implements the use case - tracking USB stick event detection from dmesg logs
# 
# each event are tracked ty 2 lines in logs:
# [  198.007528] usb 3-2: Product: Mass Storage Device
# [  199.309030]  sda: sda1
# 
# first line indicates that we've got a USB mass storage
# second line show the /dev/ device name for this USB storage
#
# Usage:
#  ./parse_usb.py <log_filename>


import re
import types
import argparse
from parse_lib import *

############## main body
# first check script's arguments
args_parser = argparse.ArgumentParser(description="parse kernel logs (dmesg) to find USB storage detection")
args_parser.add_argument("file", help="log filename")
args = args_parser.parse_args()


# config log parser
# define function that will parse out the device name

# \brief handler function that search for device name in the log line
# \params line - the log line to check
# \return the text to print on output if log detected
def parse_devname(line):
   pattern = re.compile(r"(?P<time>\[\ *.*\])\ *sd[a-zA-Z]:\ (?P<devname>.*)", re.VERBOSE)
   match = pattern.search(line)
   if match: return "{} USB storage detected: {}".format(match.group("time"),match.group("devname"))

# actually register a parser for 2 lines log
# first line will be handled using in-built regexp
# second line will be handled by our function
parser_usb = Parser([r"usb.*Product:\ Mass\ Storage\ Device",parse_devname])

# now go throught input file
# TODO support run with input stream, like 'dmesg|parse_logs.py'
filename = args.file
with open(filename, "r", encoding='utf-8', errors='ignore') as fp:
   line_num = 0
   for line in fp:
      line_num += 1
      res = parser_usb.parse(line)
      # if event is detected in the log - print file and line number and actual report
      if res:
         print ("{} +{:<3} {}".format(filename, line_num, res))
