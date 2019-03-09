#see https://stackoverflow.com/questions/2081836/reading-specific-lines-only
import sched, time, threading

s = sched.scheduler(time.time, time.sleep)
lastIndex = 0

def main ():
	s.enter(3,1,readFile,())
	s.run()

def readFile():
	global lastIndex
	print("checking for updates passed line " + str(lastIndex))
	file = open("sample.txt")
	for i, line in enumerate(file):
		if (i > lastIndex):
			print("NEW " + line)
			lastIndex = i

	print("closing file.")
	file.close()
	s.enter(3,1,readFile,())

#run the main method
main()
