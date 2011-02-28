#!/usr/bin/python
from optparse import OptionParser
from stat import ST_MODE
from stat import S_IWRITE
import os
import subprocess

def search_and_replace_in_file(path, oldstr, newstr):
    """
    Replace all instances of oldstr with newstr in the file found at path
    """
    f = open(path, "r")
    text = f.read()
    f.close()
    f = open(path, "w")
    f.write(text.replace(oldstr, newstr))
    f.close()

def rmrf_dir(path):
    """
    Recursively delete everything under a subdir. Use with care
    """
    for root, dirs, files in os.walk(".git", topdown=False):
        for f in files:
	    p = os.path.join(root,f)
	    os.chmod(p, os.stat(p)[ST_MODE] | S_IWRITE)
	    os.remove(p)
        for d in dirs:
	    p = os.path.join(root,d)
	    os.chmod(p, os.stat(p)[ST_MODE] | S_IWRITE)
	    os.rmdir(p)
    os.rmdir(path)


if __name__ == "__main__":
    optparser = OptionParser(usage="usage: %prog original_path new_name")

    (options, args) = optparser.parse_args()

    if len(args) != 2:
        optparser.error("incorrect number of arguments")

    print """
-------------------------------------------------------
This script will rename  a repository and  restart  its
history. It will remove any  local  changes/history you 
have made to the repository.
-------------------------------------------------------
"""

    x = raw_input("Do you want to continue?")
    if (not x in ["y","Y","yes","Yes","YES"]):
        exit(1)
    

    original = os.path.abspath(args[0])
    newname = args[1]
        
    (parent_path, oldname) = os.path.split(original)
    new_path = os.path.join(parent_path, newname)
    
    print "Renaming %s to %s" % (original, new_path)

    os.rename(original, new_path)

    os.chdir(new_path)    

    print "Re-init git"
    rmrf_dir(".git")
    os.system("git init")
    
    new_remote = 'ssh://git@github.com:22/xcore/%s.git' % newname
    print "Changing remote origin of git repository to:\n%s" % new_remote
    os.system('git remote add origin %s' % new_remote)

    print "Updating eclipse projects"

    search_and_replace_in_file(".project",oldname, newname)
    search_and_replace_in_file(".cproject",oldname, newname)
