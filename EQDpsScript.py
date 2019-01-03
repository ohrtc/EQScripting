import re, datetime, calendar, time, json

damageWords = ["pierces","slashes","crushes","bashes","backstabs","kicks","bash","slash","crush"]
monthAbbrDict = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
COMBAT_TIMEOUT = 10

eqSessions = []	#list of all total sessions between "Welcome to Everquest" logins
currentEncounter = Encounter()	#current combat encounter. Contains list of enemies and damage done.
currentSession = Session()	#current session. Contains list of encounters.

class Line(object):
	def __init__(self):
		self.time = None
		self.text = None	#full text of the line
		self.words = []		#list of words in the line
	#ToString
	#def __repr__(self):
	#	return str(self.time) + " " + str(self.text)

class Session(object):
	def __init__(self):
		self.start = None
		self.end = None
		self.encounters = []

class Encounter(object):
	def __init__(self):
		self.start = None
		self.end = None
		self.lastDamageTime = datetime.datetime(1970,1,1,0,0,0)
		self.enemies = {}
	
def validateAndCreateLine (line):
	currentLine = Line()
	line = line.strip()
	if (line):	#Some output has no words. Skip it.
		pattern = re.compile(r"\[(.*?)\]\s(.*)")
		matchObj = pattern.search(line)
		eventFrag = matchObj.group(2)	#take event fragment string as is
		dateToken = matchObj.group(1)	#parse date string into datetime obj
		dateTokens = dateToken.split()
		timeVal = dateTokens[3].split(":")
		dateFrag = datetime.datetime(int(dateTokens[4]),monthAbbrDict[dateTokens[1]],int(dateTokens[2]), int(timeVal[0]), int(timeVal[1]), int(timeVal[2]))
		currentLine.time = dateFrag
		currentLine.text = eventFrag
		currentLine.words = re.split(r" ",eventFrag)
		if (len(currentLine.words) > 1):	#some output only has one word. Skip it.
			return currentLine
	return False

def saveAndResetSession(time):
	global eqSessions, currentEncounter, currentSession
	#TODO: calculate total damage/DPS for the session.
	#before reseting the session we should save off the "running" encounter
	saveAndResetEncounter(time)
	currentSession.end = time
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
		line = validateAndCreateLine(unparsedLine)
		if (line): #line is valid!
		
			if(currentSession.start == None): 
				#this must be the first session in the file.
				currentSession.start = line.time		
			if (line.text == "Welcome to EverQuest!" and currentSession.end != None): 
				#this is not the first session. Save currentSession and start a new one.
				saveAndResetSession(line.time)
				continue
			
			#check second word to see if this is a damage event
			for damageWord in damageWords:
				if line.words[1] == damageWord:
					
					#if nothing had been damaged the last COMBAT_TIMEOUT seconds this is a new encounter.
					if ((line.time - currentEncounter.lastDamageTime).total_seconds() > COMBAT_TIMEOUT): 
						saveAndResetEncounter(line.time)
						
					currentEncounter.lastDamageTime = line.time	#update running combat time
					damage = int(re.findall(r'\d+',line.text)[0])	#search for the integer in the damage event
					enemyName = " ".join(line.words[2:line.words.index('for')])	#search for enemy name in the damage event
					
					if enemyName not in currentEncounter.enemies:
						#this is the first instance of damage to this enemy in the encounter
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

#run the main method
getTotalDamage("C:\P99\Logs\eqlog_Ohmi_project1999.txt")