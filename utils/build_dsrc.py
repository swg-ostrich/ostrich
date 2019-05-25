#!/usr/bin/python
# Created by seefo 
import Queue as queue
import os
import os.path
import subprocess
import sys
import threading
import time
import datetime
import copy

q = queue.Queue()
completedFileCount = 0
completedFiles = []
failedTasks = []
lastTickStatus = lambda: None

def displayQueueStatus():
	while q.qsize() > 0:
		completedTasks = totalTaskCount - q.qsize()
		progressPercent = (float(completedTasks) / float(totalTaskCount)) * 100.0
		
		# get stats between last tick
		tasksCompletedSinceLastTick = completedTasks - lastTickStatus.completedTasks
		timeSinceLastTick = time.time() - lastTickStatus.time
		
		# calculate eta
		speed = float(tasksCompletedSinceLastTick) / float(timeSinceLastTick)
		eta = float(q.qsize()) / max(speed, 1)
		
		# update tick object
		if timeSinceLastTick >= lastTickSampleRate:
			lastTickStatus.completedTasks = completedTasks
			lastTickStatus.time = time.time()

		# print current progress
		print '\x1b[2K\r', "Progress: %.2f%% [%d / %d] ETA %s (%d tasks/second)" % (progressPercent , completedTasks, totalTaskCount, str(datetime.timedelta(seconds=eta)).split(".")[0], speed),
		sys.stdout.flush()
		time.sleep(1)
	q.join()

def processTask( task ):
	toolCmd = task[0]
	srcFile = task[1]
	dstFile = task[2]

	if srcFile in completedFiles:
		return

	# remove dst file so we can validate successful creation
	if os.path.isfile(dstFile):
		os.remove(dstFile)

	# run the tool
	cmd = toolCmd.replace("$srcFile", srcFile)

	# make sure destination folder exists
	dstFolder = os.path.dirname(dstFile)
	try:
		if not os.path.exists(dstFolder):
			os.makedirs(dstFolder)
	except:
		pass

	if displayCmdOutput:
		retcode = subprocess.call(cmd, shell=True, stderr=subprocess.STDOUT)
	else:
		FNULL = open(os.devnull, 'w')
		retcode = subprocess.call(cmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

	# validate dst file was successfully created and no errorcode
	if os.path.isfile(dstFile) is False or retcode is not 0:
		failedTasks.append(task)
	else:
		global completedFileCount
		completedFileCount += 1

	completedFiles.append(srcFile)

def queueWorker():
	while True:
		task = q.get()
		processTask(task)
		q.task_done()


def startQueueWorkers():
	for i in range(numberOfWorkerThreads):
		t = threading.Thread(target=queueWorker)
		t.daemon = True
		t.start()

def walkAndCompareAndRun( src, dst, srcExt, dstExt, runCmd ):
	for root, dirs, files in os.walk(src):
		path = root.split(os.sep)

		for f in files:
			file = "%s/%s" % (root, f)
			ext = os.path.splitext(file)[1]

			if ext == srcExt and not file in ignoredFiles:
				dstFile = file.replace(src, dst).replace(srcExt, dstExt)

				if os.path.isfile(dstFile): 
					srcStat = os.stat(file)
					dstStat = os.stat(dstFile)
					
					if srcStat.st_mtime > dstStat.st_mtime or buildAllFiles:
						print "FILE %s NEEDS TO BE REBUILT" % (file)
						q.put([runCmd, file, dstFile])

				else:
					print "FILE %s NEEDS TO BE BUILT" % (file)
					q.put([runCmd, file, dstFile])

# program settings
numberOfWorkerThreads = 8  # number of concurrent builder threads
lastTickSampleRate = 10     # sample rate in seconds, for eta/speed
buildAllFiles = False       # enable to skip modification time comparison
displayCmdOutput = False    # enable to display output of tools

ignoredFiles = [
	"./dsrc/sku.0/sys.shared/built/game/misc/quest_crc_string_table.tab",
	"./dsrc/sku.0/sys.server/built/game/misc/object_template_crc_string_table.tab",
	"./dsrc/sku.0/sys.client/built/game/misc/object_template_crc_string_table.tab"
]

# build datatables
walkAndCompareAndRun( "./dsrc/sku.0/", 
					  "./data/sku.0/", 
					  ".tab", 
					  ".iff", 
					  "./configs/bin/DataTableTool -i $srcFile -- -s SharedFile searchPath10=data/sku.0/sys.shared/compiled/game searchPath10=data/sku.0/sys.server/compiled/game")

# build objects
walkAndCompareAndRun( "./dsrc/sku.0/", 
					  "./data/sku.0/", 
					  ".tpf", 
					  ".iff", 
					  "./configs/bin/TemplateCompiler -compile $srcFile")

# build scripts
walkAndCompareAndRun( "./dsrc/sku.0/sys.server/compiled/game/script", 
					  "./data/sku.0/sys.server/compiled/game/script", 
					  ".java", 
					  ".class", 
					  "javac -Xlint:-options -encoding utf8 -classpath data/sku.0/sys.server/compiled/game -d data/sku.0/sys.server/compiled/game -sourcepath dsrc/sku.0/sys.server/compiled/game -g -deprecation $srcFile")

# prepare to start working
totalTaskCount = q.qsize()
print "[***] Need to process %d build tasks" % (totalTaskCount)
startQueueWorkers()

start = time.time()
lastTickStatus.completedTasks = 0
lastTickStatus.time = start 

# start processing our queue of build tasks while there are tasks
displayQueueStatus()

# reprocess failed tasks incase it was the result of a dependency issue
if len(failedTasks) > 0:
	previousFailedTaskCount = len(failedTasks) + 1

	while previousFailedTaskCount > len(failedTasks):
		previousFailedTaskCount = len(failedTasks)
		failedTasksCopy = copy.deepcopy(failedTasks)

		completedFiles = []
		failedTasks = []

		for task in failedTasksCopy:
			q.put(task)

		displayQueueStatus()

	# no more files were built so prepare for final output
	if len(failedTasks) == previousFailedTaskCount: print ""


# display our final results
end = time.time()
print "[***] Successfully built %d files in %d seconds" % (completedFileCount, end - start)

# display results
print "[***] Failed to build %d tasks" % (len(failedTasks))
for task in failedTasks: print "FAILED TO BUILD %s" % (task[1])
