#!/usr/bin/env python

"""ImageSweep.py: Deletes unnecessary image drawables.."""

__author__      = "Josh Ruesch"
__copyright__   = "Copyright 2014, Instructure Inc"

import os
import re
import sys
import shutil

#Global variables.
used_drawable_files = set()
files_deleted = 0
mega_bytes_deleted = 0

#Naive method to determine if a directory is an android /res folder.
def isResourceRoot(directory):
  return (
  (os.path.exists(directory+"/drawable"))        or
  (os.path.exists(directory+"/drawable-ldpi"))   or
  (os.path.exists(directory+"/drawable-mdpi"))   or
  (os.path.exists(directory+"/drawable-hdpi"))   or
  (os.path.exists(directory+"/drawable-xhdpi"))  or
  (os.path.exists(directory+"/drawable-xxhdpi")) or
  (os.path.exists(directory+"/drawable-xxxhdpi")))

#We only want to remove unused PICTURES (pngs)
def addFile(fileName):
  fileName = fileName.replace("R.drawable.", "").replace("@drawable/","")
  used_drawable_files.add(fileName + ".png")

#Check to see what resources are referenced in this function.
def checkFileForResources(fileAsString):
  file = open(fileAsString, 'r')
  contents = file.read()
  file.close()

  #Handle code files.
  pattern = re.compile('R.drawable.[a-zA-Z0-9_]*')
  results = pattern.findall(contents)
  for result in results:
    addFile(result)

  #Handle layout files.
  pattern = re.compile('@drawable/[a-zA-Z0-9_]*')
  results = pattern.findall(contents)
  for result in results:
    addFile(result)

#We only want to if it's an unreferenced PNG.
def deleteIfUnusedPNG(directory, fileName):
    if fileName.endswith(".png") and not fileName.endswith(".9.png"):
      if fileName not in used_drawable_files:
        global files_deleted
        global mega_bytes_deleted

        #Do stats tracking.
        files_deleted += 1
        current_file_size = os.path.getsize(directory+"/"+fileName) / 1024.0 / 1024.0
        mega_bytes_deleted += current_file_size

        #Actually delete the file.
        os.unlink(directory+"/"+fileName)
        print ("Deleted (%.2f Mbs): " + directory+"/"+fileName) % current_file_size

def moveUnusedPNG(directory, fileName, dest):
    if fileName.endswith(".png") and not fileName.endswith(".9.png"):
      if fileName not in used_drawable_files:
        global files_deleted
        global mega_bytes_deleted

        #Do stats tracking.
        files_deleted += 1
        current_file_size = os.path.getsize(directory+"/"+fileName) / 1024.0 / 1024.0
        mega_bytes_deleted += current_file_size


        # move file
        if not os.path.isdir(dest+"/"+directory):
          os.makedirs(dest+"/"+directory)
        shutil.move(directory + "/" + fileName, dest+"/"+directory)

        print ("Moved (%.2f Mbs): " + directory+"/"+fileName) % current_file_size

##########
## MAIN ##
##########

#Make sure they passed in a project source directory.
num_args = len(sys.argv)
if not num_args >= 2:
  print 'Usage: "python ImageSweep.py project_src_directory destination_directory" (%d) found ' % num_args
  quit()

rootDirectory = sys.argv[1]
destDirectory = "res_backup"
if num_args > 2 :
  destDirectory = sys.argv[2]

resDirectory = rootDirectory

#Figure out which resources are actually used.
for root, dirs, files in os.walk(rootDirectory):
  if isResourceRoot(root):
    resDirectory = root

  for file in files:
    checkFileForResources(root+"/"+file)

if num_args == 2:
  #Delete the unused pngs.
  for root, dirs, files in os.walk(resDirectory):
      for file in files:
        # deleteIfUnusedPNG(root, file)
elif num_args == 3:
  #move the files
  for root, dirs, files in os.walk(resDirectory):
      for file in files:
        moveUnusedPNG(root, file, destDirectory)

#Print out how many files were actually deleted.
print ""
print "%d file(s) %s" % (files_deleted, num_args == 2 ? "deleted." : "moved.")
print "%.2f megabytes freed" % (mega_bytes_deleted)
