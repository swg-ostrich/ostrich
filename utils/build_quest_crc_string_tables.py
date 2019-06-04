#!/usr/bin/env python

from os import walk, path, makedirs
from subprocess import PIPE, Popen

def read_objects(objectdir):
	files = []

	for (dirname, dirnames, filenames) in walk(objectdir):
		for filename in filenames:
			filename = filename.replace('.iff', '')

			objfile = path.join(dirname, filename)
			objfile = objfile.replace("%s/" % objectdir, '')

			files.append(objfile)

	return files

allobjs = []
	
skus = next(walk('content'))[1]
skus.sort()

for sku in skus:
	questlistdir = './content/%s/data/sys.shared/compiled/game/datatables/questlist' % (sku)
	allobjs.extend(read_objects(questlistdir))

allobjs.sort()

tabfile = './content/sku.0/dsrc/sys.shared/built/game/misc/quest_crc_string_table.tab'
ifffile = './content/sku.0/data/sys.shared/built/game/misc/quest_crc_string_table.iff'

if not path.exists(path.dirname(tabfile)):
	makedirs(path.dirname(tabfile))

if not path.exists(path.dirname(ifffile)):
	makedirs(path.dirname(ifffile))

crc_call = ['./tools/buildCrcStringTable.pl',  '-t', tabfile, ifffile]

p = Popen(crc_call, stdin=PIPE, stdout=PIPE)

for obj in allobjs:
	p.stdin.write(obj + '\n')

p.communicate()
