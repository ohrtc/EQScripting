#see https://stackoverflow.com/questions/2081836/reading-specific-lines-only
import sched, time, threading, pyrebase, re, datetime, calendar, time, sys, sched, time, threading

"""
# These are class definitions used throughout the script.
"""
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
		self.playersInvolved = {} #{key=playerName(str),value=DamageTime(obj)}

class Encounter(object):
	def __init__(self):
		self.start = None
		self.end = None
		self.lastDamageTime = datetime.datetime(1970,1,1,0,0,0)
		self.enemies = {}	#{key=enemyName(str), value={key=playerName(str),damage(int)}
		self.playersInvolved = {} #{key=playerName(str), value=DamageTime(obj)}

class DamageTime(object):
	def __init__(self):
		self.damageDone = 0
		self.combatTime = 0
		self.dps = 0

	def __init__(self, initialDamage):
		self.damageDone = initialDamage
		self.combatTime = 0
		self.dps = 0

"""
# These are global variables used throughout the script.
"""
damageWords = ["pierces","slashes","punches","crushes","bashes","backstabs","kicks","slices",
				"pierce",  "slash",  "punch",  "crush",  "bash", "backstab","kick",  "slice"]
monthAbbrDict = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
COMBAT_TIMEOUT = 10

eqSessions = []	#list of all total sessions between "Welcome to Everquest" logins
currentEncounter = Encounter()	#current combat encounter. Contains list of enemies and damage done.
currentSession = Session()	#current session. Contains list of encounters.

s = sched.scheduler(time.time, time.sleep) #instance of a scheduler to manipulate later
lastIndex = 0

db = None

defaultFile = "./sample_input_data/sample_test.txt"

"""
# These are helper functions used within the script and are not meant to be called from the main()
# function definition.
"""

##Helper code for firebase
def firebase_setup():
    txt = open("api_key.txt")
    config = {
        "apiKey": txt.read(),
        "authDomain": "testprojectforeq.firebaseapp.com",
        "databaseURL": "https://testprojectforeq.firebaseio.com",
        "storageBucket": "testprojectforeq.appspot.com",
        "serviceAccount": "serviceCredentials.json"
    }
    return pyrebase.initialize_app(config)
#data = {"sessionStart": "2019-05-22 11:39:49" , "sessionEnd": "2019-05-22 12:39:49"}
#db.child("sessions").push(data)


def pushEncounter(encounter, sessionKey):
    global db
    
	#print ("\n" + str(encounter.start) + " to " + str(encounter.end))
	#for enemy,player in encounter.enemies.items():
	#	formattedEnemy = '{:>30}'.format(enemy)
	#	print (formattedEnemy + "\t" + str(player))
	#for player in encounter.playersInvolved:
	#	formattedPlayer = '{:>30}'.format(player)
	#	print (formattedPlayer + ": " + str(encounter.playersInvolved[player].dps))

def printEncounter(encounter):
	print ("\n" + str(encounter.start) + " to " + str(encounter.end))
	for enemy,player in encounter.enemies.items():
		formattedEnemy = '{:>30}'.format(enemy)
		print (formattedEnemy + "\t" + str(player))
	for player in encounter.playersInvolved:
		formattedPlayer = '{:>30}'.format(player)
		print (formattedPlayer + ": " + str(encounter.playersInvolved[player].dps))

def pushSession(session):
    global db
	#print ("\n------------------------------------------------------")
	#print ("START " + str(session.start) + "  to  END " + str(session.end))
	#for playerName in session.playersInvolved:
	#	player = session.playersInvolved[playerName]
	#	formattedPlayer = '{:>30}'.format(playerName)
	#	print (formattedPlayer + ": (TOTAL DAMAGE: " + str(player.damageDone) + "\t TOTAL TIME: " + str(player.combatTime) + " \t DPS: " + str(player.dps))
	#print ("------------------------------------------------------")

def printSession(session):
	print ("\n------------------------------------------------------")
	print ("START " + str(session.start) + "  to  END " + str(session.end))
	for playerName in session.playersInvolved:
		player = session.playersInvolved[playerName]
		formattedPlayer = '{:>30}'.format(playerName)
		print (formattedPlayer + ": (TOTAL DAMAGE: " + str(player.damageDone) + "\t TOTAL TIME: " + str(player.combatTime) + " \t DPS: " + str(player.dps))
	print ("------------------------------------------------------")

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

def saveAndResetSession(nextSessionStartTime):
	#print("Saving current session and resetting currentSession variable")
	global eqSessions, currentEncounter, currentSession
	#before reseting the session we should save off the "running" encounter
	saveAndResetEncounter()
	for playerName in currentSession.playersInvolved:
		player = currentSession.playersInvolved[playerName]
		if player.combatTime == 0:
			del player
			#currentSessions.playersInvolved[playerName]
		else:
			player.dps = player.damageDone/player.combatTime

	eqSessions.append(currentSession)
	currentSession = Session()
	currentSession.start = nextSessionStartTime

def saveAndResetEncounter():
	#print("Saving current encounter and resetting currentEncounter variable")
	global eqSessions, currentEncounter, currentSession
	if(currentEncounter.start != None):
		inCombatTime = (currentEncounter.lastDamageTime - currentEncounter.start).total_seconds()
		#print(inCombatTime)
		if(inCombatTime != 0):
			for playerName in currentEncounter.playersInvolved:
				player = currentEncounter.playersInvolved[playerName]
				player.combatTime = inCombatTime
				player.dps = player.damageDone/inCombatTime
				currentSession.playersInvolved[playerName].combatTime += inCombatTime
			currentEncounter.end = currentEncounter.lastDamageTime
			currentSession.encounters.append(currentEncounter)
			printEncounter(currentEncounter)
            pushEncounter(currentEncounter, str(currentEncounter.start))
	currentEncounter = Encounter()

def processDamageLine(line):
	#if nothing had been damaged the last COMBAT_TIMEOUT seconds this is a new encounter.
	if(currentEncounter.start == None):
		currentEncounter.start = line.time
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

	if playerName in currentEncounter.playersInvolved:
		currentEncounter.playersInvolved[playerName].damageDone += damage
	else:
		currentEncounter.playersInvolved[playerName] = DamageTime(damage)

	if playerName in currentSession.playersInvolved:
		currentSession.playersInvolved[playerName].damageDone += damage
	else:
		currentSession.playersInvolved[playerName] = DamageTime(damage)

def processLine(lineObj):
	global damageWords, eqSessions, currentEncounter, currentSession
	if (lineObj): #line is valid!
		if(currentSession.start == None):
			#this must be the first session in the file.
			currentSession.start = lineObj.time
		if (lineObj.text == "Welcome to EverQuest!" and currentSession.end != None):
			#this is not the first session. Save currentSession and start a new one.
			saveAndResetSession(lineObj.time)
			#continue
		currentSession.end = lineObj.time
		#Check, if there is a currentEncounter running, and it has been COMBAT_TIMEOUT seconds since last damage, then we should save it and reset the variable
		if(currentEncounter.start != None and currentEncounter.end == None):
			if ((lineObj.time - currentEncounter.lastDamageTime).total_seconds() > COMBAT_TIMEOUT):
				saveAndResetEncounter()
		for damageWord in damageWords:
			#check second word to see if this is a damage event
			if lineObj.words[1] == damageWord:
				processDamageLine(lineObj)

def readFile(filename):
	global lastIndex
	#print("checking for updates passed line " + str(lastIndex))
	file = open(filename)
	for i, line in enumerate(file):
		if (i > lastIndex):
			##TODO - replace simple print statement with parsing logic.
			#print("NEW " + line)
			lineObj = validateAndCreateLine(line)
			processLine(lineObj)
			lastIndex = i
	#print("closing file.")
	file.close()
	s.enter(10,1,readFile,kwargs={"filename": filename})

def parseFile(filename):
	#temp until we get the live looping parsing implemented
	s.enter(10,1,readFile,kwargs={"filename": filename})
	s.run()

#main method in which arguments are parsed. the first argument is always the name of the file ran (in this case, main.py)
def main():
    firebase = firebase_setup()
    global db
    db = firebase.database()
    print("Firebase db is setup.")
    if(len(sys.argv) < 2):
        print("Running against default sample file.")
        parseFile(defaultFile)
    else:
        filename = sys.argv[1]
        print("Running against file: " + filename)
        parseFile(filename)

#run the main method
main()
