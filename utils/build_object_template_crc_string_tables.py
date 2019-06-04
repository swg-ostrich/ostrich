#!/usr/bin/env python
from os import walk, path, makedirs
from subprocess import PIPE, Popen

serverobjs = []
sharedobjs = []
allobjs = []

def read_objects(objectdir):
	files = []

	for (dirname, dirnames, filenames) in walk(objectdir):
		for filename in filenames:
			if '.iff' in filename:
				objfile = path.join(dirname, filename)
				objfile = objfile.replace(objectdir.split('/object')[0] + '/', '')

				files.append(objfile)

	return files

def build_skus():
	skus = next(walk('content'))[1]
	skus.sort()
	
	for sku in skus:
		serverobjs.extend(read_objects('./content/%s/data/sys.server/compiled/game/object' % (sku)))
		sharedobjs.extend(read_objects('./content/%s/data/sys.shared/compiled/game/object' % (sku)))
		sharedobjs.extend(read_objects('./content/%s/data/sys.server/compiled/game/object/creature/player' % (sku)))
		
		allobjs.extend(serverobjs)
		allobjs.extend(sharedobjs)
	
	build_table('client', sharedobjs)
	build_table('server', list(set(allobjs)))

	
def build_table(type, objs):
	tabfile = "./content/sku.0/dsrc/sys.%s/built/game/misc/object_template_crc_string_table.tab" % (type)
	ifffile = "./content/sku.0/data/sys.%s/built/game/misc/object_template_crc_string_table.iff" % (type)

	if not path.exists(path.dirname(tabfile)):
		makedirs(path.dirname(tabfile))

	if not path.exists(path.dirname(ifffile)):
		makedirs(path.dirname(ifffile))

	crc_call = ['./tools/buildCrcStringTable.pl',  '-t', tabfile, ifffile]

	p = Popen(crc_call, stdin=PIPE, stdout=PIPE)

	for obj in sorted(objs):
		p.stdin.write(obj + '\n')

	p.communicate()

build_skus()