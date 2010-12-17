#!/usr/bin/python
# coding: utf-8

import sys
sys.path.append('/tools/python/lib/python')

from zipfile import ZipFile
import sys, os, glob, re,datetime, xml.dom.minidom

if len(sys.argv) < 2:
    print "Usage: validate_spec file"
    exit(1)

"""
Validate a spec rst into the product database
"""

import testplan

# Import Directive base class.


spec_file = sys.argv[1]

description = ('Validates a .rst spec file')
from docutils.parsers.rst import directives


print "Parsing spec..."

#valid, err_msg, parsed = testplan.parse_testplan_file(spec_file)
valid, err_msg, parsed = testplan.parse_testplan_string(open(spec_file).read())
    
print err_msg

if valid:
    print "Valid spec document\n"
else:
    print "ERRORS in document\n"

