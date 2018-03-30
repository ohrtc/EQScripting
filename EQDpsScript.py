import re, datetime, calendar, time

damageWords = ["pierces","slashes","crushes","scores","bashes","backstabs","kicks","bash","slash","bashes"]
monthAbbrDict = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
eqSessions = []

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
	party = {}
	currentSession = {"Start Datetime": None, "End Datetime": None}
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
				if(currentSession["Start Datetime"] is None):
					currentSession["Start Datetime"] = tokens[0]
					if (tokens[1] == "Welcome to EverQuest!"):
						continue
				if (tokens[1] == "Welcome to EverQuest!"):
					currentSession["Party"] = party
					eqSessions.append(currentSession)
					#need to reinstatiate currentSession object? reference or value?
					currentSession = {"Start Datetime" : tokens[0]}
					party = {}
					continue
				#check second word to see if this is a damage event
				for damageWord in damageWords:
					if eventWords[1] == damageWord:
						#DEBUG
						#print(tokens[0])
						#print("Found match: " + tokens[1])
						
						#search for the integer in the damage event
						damage = int(re.findall(r'\d+',tokens[1])[0])
						#Assumption that eventWords[0] is a player name
						if eventWords[0] in party:
							party[eventWords[0]] += damage
						else:
							party[eventWords[0]] = damage
						currentSession["End Datetime"] = tokens[0]
						break
	#after last line, add party to current session, add current session to eqSession list
	currentSession["Party"] = party
	eqSessions.append(currentSession)
	for item in eqSessions:
		print(str(item))
	
	#for member in party:
	#	print("Character:   " + member)
	#	print("Damage Done: " + str(party[member]))
	#	print("")
	file.close()

print("============Running Main Script============")
getTotalDamage("321.txt")
print("\n")
