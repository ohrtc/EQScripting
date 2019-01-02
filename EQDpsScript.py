import re, datetime, calendar, time, json

damageWords = ["pierces","slashes","crushes","bashes","backstabs","kicks","bash","slash","crush"]
monthAbbrDict = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}

COMBAT_TIMEOUT = 10

class Line():
	time = None
	text = None #Full text of the line
	words = [] #List of words in the line
	#ToString
	def __repr__(self):
		return str(self.time) + " " + str(self.text)

class Session():
	start = None
	end = None
	encounters = []
	
	#ToString
	def __repr__(self):
		return "START: " + str(self.start) + "\tEND " + str(self.end) + "\n" + str(self.encounters) + "\n"

class Encounter():
	start = None
	end = None
	lastDamageTime = datetime.datetime(1970,1,1,0,0,0)
	enemies = {}
	
	#ToString
	def __repr__(self):
		return "\n\n" + str(self.start) + " to " + str(self.end) + "\t" + str(self.enemies)

#class Party():
#	name = None
#	damage = None
#	DPS = None
	
#	def __repr__(self):
#		name = '{:>30}'.format(self.name)
#		return "\n" + name + " " + str(self.damage)
	
eqSessions = [] #list of all total sessions between "Welcome to Everquest" logins
currentEncounter = Encounter() #mobs currently alive
currentSession = Session()

def lineToDatetimeEventTuple (line):
	pattern = re.compile(r"\[(.*?)\]\s(.*)")
	matchObj = pattern.search(line)
	#take event fragment string as is
	eventFrag = matchObj.group(2)
	#parse date string into datetime obj
	dateToken = matchObj.group(1)
	dateTokens = dateToken.split()
	timeVal = dateTokens[3].split(":")
	dateFrag = datetime.datetime(int(dateTokens[4]),monthAbbrDict[dateTokens[1]],int(dateTokens[2]), int(timeVal[0]), int(timeVal[1]), int(timeVal[2]))
	dateEventTuple = (dateFrag, eventFrag)
	return dateEventTuple
	
def resetSessionVariables(start):
	global eqSessions, currentEncounter, currentSession
	
	#TODO: calculate total damage/DPS for the session.
	eqSessions.append(currentSession)

	#Check any loose encounters (no slain event)
	#print("--DEBUG	Current Enemies (should be blank!)	" + str(tokens[0]) + "\n" + str(currentEncounters))
	currentEncounter = Encounter()
	
	#need to reinstatiate currentSession object? reference or value?
	currentSession = Session()
	currentSession.encounters = []
	currentSession.start = start
	
def validateAndTokenize(line):
	currentLine = Line()
	strippedStr = line.strip()
	if strippedStr: #Some output has no words. Skip it.
		#tokenize dates to tokens[0] and event text to tokens[1]
		tokens = lineToDatetimeEventTuple(line)
		
		currentLine.time = tokens[0]
		currentLine.text = tokens[1]
		#parse event text to individual words
		currentLine.words = re.split(r" ",tokens[1])
		if len(currentLine.words) > 1: #some output only has one word. Skip it.
			return currentLine

	return False

def getTotalDamage (filename):
	global eqSessions, currentEncounter, currentSession
	
	file = open(filename)

	for unparsedLine in file:
		line = validateAndTokenize(unparsedLine)
		if (line): #line is valid!
			if(currentSession.start == None): #this must be the first session in the file.
				currentSession.start = line.time
			if (line.text == "Welcome to EverQuest!" and currentSession.end != None): #this is not the first session. Append previous.
				resetSessionVariables(line.time)
				continue
			
			#check second word to see if this is a damage event
			for damageWord in damageWords:
				if line.words[1] == damageWord:
					
					#print(line.time - currentEncounter.lastDamageTime)
					#if nothing had been damaged the last COMBAT_TIMEOUT seconds this is a new encounter.
					if ((line.time - currentEncounter.lastDamageTime).total_seconds() > COMBAT_TIMEOUT): 
						if(currentEncounter.start != None):
							#append previous encounter to session. Reset current encounter.
							currentEncounter.end = currentEncounter.lastDamageTime
							currentSession.encounters.append(currentEncounter)
						
						#TODO check if there are enemies that had not been slain? 
						currentEncounter = Encounter()
						currentEncounter.enemies = {}
						currentEncounter.start = line.time
						
					currentEncounter.lastDamageTime = line.time
				
					#search for the integer in the damage event
					damage = int(re.findall(r'\d+',line.text)[0])
					enemyName = " ".join(line.words[2:line.words.index('for')])
					#print("enemyName: " + enemyName)
					
					if enemyName not in currentEncounter.enemies:
						currentEncounter.enemies[enemyName] = {}
					
					#Assumption that eventWords[0] is a player name
					playerName = line.words[0]
					if playerName in currentEncounter.enemies[enemyName]:
						currentEncounter.enemies[enemyName][playerName] += damage
					else:
						currentEncounter.enemies[enemyName][playerName] = damage
							
					currentSession.end = line.time
					break
				
			#check for an enemy being slain
		#	if 'slain' in line.words[2:]:
		#		if line.words[0] == 'You': #you have slain an enemy
		#			line.words[-1] = line.words[-1][:-1] #Trim exclamation mark
		#			enemyName = " ".join(line.words[3:])
		#		else: #someone else has slain an enemy
		#			slainIndex = line.words.index('slain')
		#			enemyName = " ".join(line.words[0:slainIndex-2])
		#				
		#		if enemyName in currentEncounters:
		#			#print("enemyName slain: " + enemyName)
		#			currentEncounters[enemyName].end = line.time
		#			currentSession.encounters.append(currentEncounters.pop(enemyName))
		#		else:
		#			print("--DEBUG	Enemy: " + enemyName + " was slain without damage? " + str(line.time))
			
			
	#after last line, add party to current session, add current session to eqSession list
	eqSessions.append(currentSession)
	print(eqSessions)
	x = json.dumps(eqSessions)
	print (x)
	file.close()

print("============Running Main Script============")
getTotalDamage("samples/sample_test.txt")
print("\n")