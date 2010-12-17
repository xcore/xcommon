#!/usr/bin/python
# coding: utf-8

import sys
sys.path.append('/tools/python/lib/python')

from zipfile import ZipFile
import sys, os, glob, re,datetime, xml.dom.minidom
from optparse import OptionParser

optparser = OptionParser(usage="usage: %prog [options] testplan_file spec_file"
)

optparser.add_option("-l", "--list_tests",dest='list_tests',action='store_true',default=False, help="list all expanded tests")

optparser.add_option("-u", "--uncovered",dest='uncovered',action='store_true',default=False, help="list uncovered features/configurations")

optparser.add_option("-d", "--list-defaults",dest='list_defaults',action='store_true',default=False, help="list default config options")

optparser.add_option("-s", "--summary",dest='summarize',action='store_true',default=False, help="summarize number of tests for top level features")

(options, args) = optparser.parse_args()

if len(args) != 2:
    optparser.error("incorrect number of arguments")

"""
Validate a spec rst into the product database
"""

import testplan

# Import Directive base class.


testplan_file = args[0]
spec_file = args[1]

description = ('Validates a .rst spec file')
from docutils.parsers.rst import directives


print "Parsing spec..."

valid, err_msg, parsed = testplan.parse_testplan_file(spec_file, check_errors=True)
    
print err_msg

if valid:
    print "Valid spec document"
    print str(len(parsed['feature'])) + " features."
else:
    print "ERRORS in spec document"
    exit(1)

print "Parsing testplan..."

valid, err_msg, parsed = testplan.parse_testplan_file(testplan_file, parsed, check_errors=True)

print err_msg

if not valid:
    print "ERRORS in testplan document\n"
    exit(1)
  
parsed = testplan.complete_parsed(parsed)

for f in parsed['feature']:
    for p in f.parents:
        if p.is_config_option:
            p1 = p.parents[0]
            sys.stderr.write("ERROR: Config option parent `"+str(p)+"' of  `" + str(f) +"' not allowed (used the feature '" + str(p1)+ "' instead or put it in configuration section)\n")
            exit(1)
                            
for t in parsed['test_procedure']:
    found = False
    for s in parsed['setup']:
        if (s.name == t.setup):
            found = True
    if not found:
        sys.stderr.write("ERROR: Test procedure `"+t.name+"'refers to unknown setup `"+t.setup+"'\n");
        exit(1)

for t in parsed['test']:
    found = False
    for tp in parsed['test_procedure']:
        if (tp.name == t.test_procedure):
            found = True
    if not found:
        sys.stderr.write("ERROR: Test `"+t.name+"'refers to unknown test procedure `"+t.test_procedure+"'\n");
        exit(1)
    

print "Valid testplan document\n"
parsed = testplan.complete_parsed(parsed)
print str(len(parsed['feature'])) + " features."
print str(len(parsed['test'])) + " tests."    

feature_count = {}
for f in parsed['feature']:
    feature_count[f] = 0
    #    print f.name + ":"+str([a.name for a in f.ancestors])
    
count = 0
time = 0
for test in parsed['test']:    
    for instance in test.instances():
        for f in set(instance.all_features) | set(instance.defaults):
            feature_count[f] = feature_count[f] + 1
        
        time = time + instance.test.test_time
        count = count + 1

print str(count) + " test cases.\n\n"

if (options.list_tests):
    print "Test cases:\n\n"
    for test in parsed['test']:
        for instance in test.instances():
            print instance
#            print [str(x) for x in instance.all_features]

if (options.uncovered):
    spec_features = [f for f in parsed['feature'] if not f.is_config_option and f.choices == []]

    spec_config_options = [f for f in parsed['feature'] if f.is_config_option]

    print("Uncovered features\n")
    found = False
    for f in spec_features:
        if (feature_count[f] == 0):
            print("   * " + f.name)
            found = True
    if not found:
        print("   None\n")
    print("\n")

    print("Uncovered configuration options\n")
    found = False
    for f in spec_config_options:
        if (feature_count[f] == 0):
            print("   * " + f.name)
            found = True
    if not found:
        print("   None\n")
    print("\n")
    

if (options.list_defaults):
    defaults = [f for f in parsed['feature'] if f.is_config_option and f.is_default]
    print "Config Defaults:\n"
    for f in defaults:
        print str(f)

if (options.summarize):
    print "\nTop level summary:\n"
    for f in parsed['feature']:
        if f.summarize:
            print f.name + ": " + str(feature_count[f]) + " tests"
