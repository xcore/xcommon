#!/usr/bin/python
from optparse import OptionParser
import os,re
import sys

script_path = os.path.dirname(os.path.realpath(__file__))

def make_copyright(owner):
    c = []
    f = open(script_path + "/" + "copyright_header")
    while True:
        line = f.readline()
        if (line == ''):
            break
        line = line.replace("<insert copyright holder here>", owner)
        c.append(line)
    f.close()
    return c

def has_copyright(path):
    f = open(path)
    has_copyright = False
    while not has_copyright:
        line = f.readline()
        if (line == ""):
            break
        if re.match('.*(copyright|Copyright)', line):
            has_copyright = True
            break
    f.close()
    return has_copyright
        
def has_standard_copyright(path, c):
    i = 0
    n = len(c)
    f = open(path)
    has_copyright = False
    while not has_copyright:
        line = f.readline()
        if line == '':
            break
        if line == c[i]:
            i = i + 1
            if i==n:
                has_copyright = True
                break
        else:
            i = 0
    return has_copyright


def is_source_file(fname):
    return (re.match('.*(\.xc$|\.c$|\.h$|\.S$|\.cpp$)', fname) != None)

def get_yesno():
    x = raw_input()
    if (x in ["y","Y","yes","Yes","YES"]):
        return True
    else:
        return False

def get_owner():
    license_file = open("LICENSE.txt","r")
    owner = None
    while owner == None:
        line = license_file.readline()
        if (line == ""):
            break
        m = re.match("Copyright \(c\) \d*, (.*), All rights reserved", line)
        if m:
            owner = m.groups(0)[0]
    license_file.close()
    return owner

    
def make_license(owner):
    src = open(script_path+"/SoftwareLicense.txt")
    dst = open("LICENSE.txt","w")
    while True:
        line = src.read()
        if (line == ""):
            break
        line = line.replace("<insert copyright holder here>",owner)
        dst.write(line)
    src.close()
    dst.close()

def insert_copyright(path, c):
    tmpfile_path = script_path+"/tmpfile"
    src = open(path,"r")
    tmpfile = open(tmpfile_path,"w")
    for line in c:
        tmpfile.write(line)
    tmpfile.write("\n")
    while True:
        line = src.read()
        if (line == ""):
            break
        tmpfile.write(line)
    src.close()
    tmpfile.close()
    dst = open(path,"w")
    tmpfile = open(tmpfile_path,"r")
    while True:
        line = tmpfile.read()
        if (line == ""):
            break
        dst.write(line)
    dst.close()
    tmpfile.close()
    os.remove(tmpfile_path)

    

if __name__ == "__main__":
    optparser = OptionParser(usage="usage: %prog repository_path")

    (options, args) = optparser.parse_args()

    repo_path = os.path.abspath(args[0])

    print("Checking repository at %s"%repo_path)

    os.chdir(repo_path)
    
    if os.path.isfile("LICENSE.txt"):
        owner = get_owner()
        if not owner:
            sys.stderr.write("Cannot determine copyright holder from LICENSE.txt\n")
            exit(1)
        print "Copyright holder is: %s" % owner
    else:
        print("Cannot find LICENSE.txt")
        confirm = False
        while not confirm:
            sys.stdout.write("Please enter copyright holder name: ")
            owner = raw_input()
            sys.stdout.write("Copyright holder: %s, are you sure? "%owner)
            confirm = get_yesno()
        print("Creating LICENSE.txt...")
        make_license(owner)
        print("Done.")

    standard_copyright = make_copyright(owner)

    missing_copyright_files = []
    non_standard_copyright_files = []

    for root, dirs, files in os.walk("."):        
        for fname in files:
            if is_source_file(fname):
                path = root +"/"+fname
                if has_copyright(path):
                    if not has_standard_copyright(path, standard_copyright):
                        non_standard_copyright_files.append(path)
                else:
                    missing_copyright_files.append(path)

    if missing_copyright_files != []:
        print "The following files have no copyright notice:\n"
        
        for path in missing_copyright_files:
            print "    " + path[2:]
        
        print "\nDo you want to insert copyrights? "
        insert = get_yesno()
        if insert:
            print "Inserting copyrights..."
            for path in missing_copyright_files:
                insert_copyright(path, standard_copyright)
            print "Done."

    if non_standard_copyright_files != []:
        print "The following files have a non-standard copyright notice:\n"
    
        for path in non_standard_copyright_files:
            print "    " + path[2:]

