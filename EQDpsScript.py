import re, datetime, calendar, time

damageWords = ["pierces","slashes","crushes","scores","bashes","backstabs","kicks","bash","slash","bashes"]
monthAbbrDict = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}

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
	


def getTotalDamage (filename, *names):
	file = open(filename)
	print("Opened file: " + filename)
	party = {}
	for name in names:
		party[name] = 0
	for line in file:
		#print(line)
		#tokens = line.split(r'(:.*:)')#(\[.*\])
		#regObj = re.compile(r"\]")
		strippedStr = line.strip()	
		if strippedStr:
			#print("got passed stripped str check with: " + strippedStr)
			tokens = lineToDatetimeEventTuple(line)
			
			#for token in tokens:
			#	print("Token:-" + token)
					
			for name in names:
				#firstWord = tokens[1]
				#print("First word:" + firstWord)
				if len(tokens) > 1 and re.match(name,tokens[1]):
					secondWord = re.split(r" ",tokens[1])[1]
					for word in damageWords:
						if word == secondWord:
							print(tokens[0])
							print("Found match: " + tokens[1])
							damage = int(re.findall(r'\d+',tokens[1])[0])
							party[name] += damage
							break
		
	print(party)
	file.close()

print("============Running Main Script============")
getTotalDamage("321.txt", "You", "Ayza", "Sylkyn")
print("\n")

