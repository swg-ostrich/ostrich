#!/usr/bin/python
# Created by seefo 
import StringIO
import hashlib
import argparse

import os
import os.path

hashes = { }
newFiles = { }

parser = argparse.ArgumentParser()
parser.add_argument('version', help='version to create, min is 1')
parser.add_argument('--from', dest='oldVersion', help='version to update from', default="0")
args = parser.parse_args()

def getMD5(fname):
	hash_md5 = hashlib.md5()
	with open(fname, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_md5.update(chunk)
	return hash_md5.hexdigest()

def isIgnoredDirectory(dir):
	for f in ignoredFiles:
		if f in dir:
			return True
	return False

def addFiles( src ):
	if not os.path.exists(src):
		return

	for root, dirs, files in os.walk(src):
		path = root.split(os.sep)

		for f in files:
			file = "%s/%s" % (root, f)
			ext = os.path.splitext(file)[1]

			if isIgnoredDirectory(file):
				continue

			checksum = str(getMD5(file))
			relativeFileName = file.replace(src, "")

			# update our checksum and add to patch list if file is diff
			if not file in ignoredFiles:
				if file in hashes:
					if hashes[file] not in checksum or buildRspFileAnyways:
						newFiles[relativeFileName] = file
						print "NEED TO UPDATE FILE %s" % (file)
				else:
					newFiles[relativeFileName] = file
					print "NEED TO ADD FILE %s" % (file)
				hashes[file] = checksum.strip()

def loadOldChecksums():
	if os.path.isfile(previousChecksumsFile):
		lines = tuple(open(previousChecksumsFile, 'r'))
		for line in lines:
			file, checksum = line.split(" ")
			hashes[file] = checksum.strip()

def buildRspFile():
	output = StringIO.StringIO()
	for file in newFiles:
		output.write("%s @ %s\n" % (file, newFiles[file]))
	return output.getvalue()

def buildChecksumsFile():
	output = StringIO.StringIO()
	for file in hashes:
		output.write("%s %s\n" % (file, hashes[file]))
	return output.getvalue()

def writeToFile(contents, file): 
	output = open(file, "w")
	output.write(contents)
	output.close()

# program settings
buildRspFileAnyways = False
ignoredFiles = [
	"data/sku.0/sys.client/compiled/game/appearance/",
	"data/sku.0/sys.client/compiled/game/datatables/",
	"ship_target_appearance.iff",
	"README.md",
	"LICENSE.md",
	".git"
]

fileChecksumsPath = "checksums_%s.txt" % (args.version)
fileRspPath = "patch_%s.rsp" % (args.version)

# load previous version
previousChecksumsFile = "checksums_%s.txt" % (args.oldVersion)
if args.oldVersion not in "0": loadOldChecksums()

# add client-only files
addFiles( "data/sku.0/sys.client/compiled/game/" )
addFiles( "data/sku.0/sys.client/built/game/" )
addFiles( "data/sku.0/sys.client/custom/" )

# add shared files
addFiles( "data/sku.0/sys.shared/compiled/game/" )
addFiles( "data/sku.0/sys.shared/built/game/" )

# build rsp file
buildRspFile()

# save rsp file
writeToFile(buildRspFile(), fileRspPath)

# save checksums file
writeToFile(buildChecksumsFile(), fileChecksumsPath)