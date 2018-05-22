import re, datetime, calendar, time

damageWords = ["pierces","slashes","crushes","bashes","backstabs","kicks","bash","slash","crush"]
monthAbbrDict = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
eqSessions = []

class Session():
	start = None
	end = None
	encounters = None
	
	#ToString
	def __repr__(self):
		return "START: " + str(self.start) + "\tEND " + str(self.end) + "\n" + str(self.encounters) + "\n"
	#	return
	#	return str(self.__dict__)

class Encounter():
	start = None
	end = None
	name = None
	party = None
	
	#ToString
	def __repr__(self):
		name = '{:>30}'.format(self.name)
		return name + "\t" + str(self.start) + " to " + str(self.end) + "\t" + str(self.party) + "\n"

		
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
	


def getTotalDamage (filename):
	file = open(filename)
	print("Opened file: " + filename)
	sessionEncounters = []
	currentEncounters = {}
	currentSession = Session()
	for line in file:
		#DEBUG
		#print(line)
		strippedStr = line.strip()	
		if strippedStr:
			#DEBUG 
			#print("got passed stripped str check with: " + strippedStr)
			
			#we have an actual line, tokenize to a date and text
			tokens = lineToDatetimeEventTuple(line)
			
			#DEBUG
			#for token in tokens:
			#	print("Token: " + str(token))
			#print("\n")
			
			#parse event
			eventWords = re.split(r" ",tokens[1])

			#some output only has one word?
			if len(eventWords) > 1:
				if(currentSession.start == None):
					currentSession.start = tokens[0]
					if (tokens[1] == "Welcome to EverQuest!"):
						continue
				if (tokens[1] == "Welcome to EverQuest!"):
					currentSession.encounters = sessionEncounters
					eqSessions.append(currentSession)
					
					#Check any loose encounters (no slain event)
					print("--DEBUG	Current Enemies (should be blank!)	" + str(tokens[0]) + "\n" + str(currentEncounters))
					currentEncounters = {}
					
					#reset current session encounters and current encounters
					sessionEncounters = []
					currentEncounters = {}
					#need to reinstatiate currentSession object? reference or value?
					currentSession = Session()
					currentSession.start = tokens[0]
					continue
				#check for an enemy being slain
				if 'slain' in eventWords[2:]:
					if eventWords[0] == 'You':
						#print("Found YOU slain match: " + tokens[1])
						#Trim exclamation mark
						eventWords[-1] = eventWords[-1][:-1]
						enemyName = " ".join(eventWords[3:])
					else:
						#print("Found slain match: " + tokens[1])
						slainIndex = eventWords.index('slain')
						enemyName = " ".join(eventWords[0:slainIndex-2])
						
					if enemyName in currentEncounters:
						#print("enemyName slain: " + enemyName)
						currentEncounters[enemyName].end = tokens[0]
						sessionEncounters.append(currentEncounters.pop(enemyName))
					else:
						print("--DEBUG	Enemy: " + enemyName + " was slain without damage? " + str(tokens[0]))
				
				#check second word to see if this is a damage event
				for damageWord in damageWords:
					if eventWords[1] == damageWord:
						#DEBUG
						#print(tokens[0])
						#print("Found damage match: " + tokens[1])
						
						#search for the integer in the damage event
						damage = int(re.findall(r'\d+',tokens[1])[0])
						enemyName = " ".join(eventWords[2:eventWords.index('for')])
						#print("enemyName: " + enemyName)
						
						if enemyName not in currentEncounters:
							encounter = Encounter()
							encounter.name = enemyName
							encounter.party = {}
							encounter.start = tokens[0]
							currentEncounters[enemyName] = encounter
						
						#Assumption that eventWords[0] is a player name
						if eventWords[0] in currentEncounters[enemyName].party:
							currentEncounters[enemyName].party[eventWords[0]] += damage
						else:
							currentEncounters[enemyName].party[eventWords[0]] = damage
							
						
						currentSession.end = tokens[0]
						break
	#after last line, add party to current session, add current session to eqSession list
	currentSession.encounters = sessionEncounters
	eqSessions.append(currentSession)
	
	print(eqSessions)
	
	file.close()

print("============Running Main Script============")
getTotalDamage("eqlog_Ohmi_project1999.txt")
print("\n")