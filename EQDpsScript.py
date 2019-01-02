import re, datetime, calendar, time, json

damageWords = ["pierces","slashes","crushes","bashes","backstabs","kicks","bash","slash","crush"]
monthAbbrDict = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}

COMBAT_TIMEOUT = 10

class Line(object):
	def __init__(self):
		self.time = None
		self.text = None #Full text of the line
		self.words = [] #List of words in the line
	#ToString
	#def __repr__(self):
	#	return str(self.time) + " " + str(self.text)

class Session(object):
	def __init__(self):
		self.start = None
		self.end = None
		self.encounters = []
	#ToString
	#def __repr__(self):
	#	return "START: " + str(self.start) + "\tEND " + str(self.end) + "\n" + str(self.encounters) + "\n"

class Encounter(object):
	def __init__(self):
		self.start = None
		self.end = None
		self.lastDamageTime = datetime.datetime(1970,1,1,0,0,0)
		self.enemies = {}
	#ToString
	#def __repr__(self):
	#	return "\n\n" + str(self.start) + " to " + str(self.end) + "\t" + str(self.enemies)
	
eqSessions = [] #list of all total sessions between "Welcome to Everquest" logins
currentEncounter = Encounter() #mobs currently alive
currentSession = Session()

def lineToDatetimeEventTuple (line):
	currentLine = Line()
	line = line.strip()	#strippedStr = line.strip()
	if line: #Some output has no words. Skip it.

		pattern = re.compile(r"\[(.*?)\]\s(.*)")
		matchObj = pattern.search(line)
		#take event fragment string as is
		eventFrag = matchObj.group(2)
		#parse date string into datetime obj
		dateToken = matchObj.group(1)
		dateTokens = dateToken.split()
		timeVal = dateTokens[3].split(":")
		dateFrag = datetime.datetime(int(dateTokens[4]),monthAbbrDict[dateTokens[1]],int(dateTokens[2]), int(timeVal[0]), int(timeVal[1]), int(timeVal[2]))
		currentLine.time = dateFrag
		currentLine.text = eventFrag
		currentLine.words = re.split(r" ",eventFrag)
		if len(currentLine.words) > 1: #some output only has one word. Skip it.
			return currentLine
	return False

def saveAndResetSession(time):
	global eqSessions, currentEncounter, currentSession
	#TODO: calculate total damage/DPS for the session.
	#before reseting the session we should save off the "running encounter"
	saveAndResetEncounter(time)
	eqSessions.append(currentSession)
	
	currentSession = Session()
	currentSession.start = time
	currentEncounter = Encounter()
	
def saveAndResetEncounter(time):
	global eqSessions, currentEncounter, currentSession
	#TODO calculate totaldamage/DPS for the encounter.
	if(currentEncounter.start != None):
		currentEncounter.end = currentEncounter.lastDamageTime
		currentSession.encounters.append(currentEncounter)
	currentEncounter = Encounter()
	currentEncounter.start = time

def getTotalDamage (filename):
	global eqSessions, currentEncounter, currentSession
	file = open(filename)
	for unparsedLine in file:
		line = lineToDatetimeEventTuple(unparsedLine)
		if (line): #line is valid!
		
			if(currentSession.start == None): #this must be the first session in the file.
				currentSession.start = line.time
			
			if (line.text == "Welcome to EverQuest!" and currentSession.end != None): #this is not the first session. Append previous.
				saveAndResetSession(line.time)
				continue
			
			currentSession.end = line.time
			
			#check second word to see if this is a damage event
			for damageWord in damageWords:
				if line.words[1] == damageWord:
					
					#if nothing had been damaged the last COMBAT_TIMEOUT seconds this is a new encounter.
					if ((line.time - currentEncounter.lastDamageTime).total_seconds() > COMBAT_TIMEOUT): 
						saveAndResetEncounter(line.time)
						
					currentEncounter.lastDamageTime = line.time
					damage = int(re.findall(r'\d+',line.text)[0])	#search for the integer in the damage event
					enemyName = " ".join(line.words[2:line.words.index('for')])
					
					if enemyName not in currentEncounter.enemies:
						currentEncounter.enemies[enemyName] = {}
				
					#Assumption that first word in a damage event is a player name
					playerName = line.words[0]
					if playerName in currentEncounter.enemies[enemyName]:
						currentEncounter.enemies[enemyName][playerName] += damage
					else:
						currentEncounter.enemies[enemyName][playerName] = damage
							
			
	file.close()
	#after last line save the "running" session and then output
	saveAndResetSession(line.time)
	outputSessions(eqSessions)

	
def outputSessions(sessions):
	for session in sessions:
		print ("\n------------------------------------------------------")
		print ("START " + str(session.start) + "  to  END " + str(session.end))
		print ("------------------------------------------------------")
		for encounter in session.encounters:
			print (str(encounter.start) + " to " + str(encounter.end))
			for enemy,player in encounter.enemies.items():
				formattedEnemy = '{:>30}'.format(enemy)
				print (formattedEnemy + "\t" + str(player))

print("============Running Main Script============")
getTotalDamage("samples/sample_medium_Ohmi.txt")
print("\n")