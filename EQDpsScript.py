import re

damageWords = ["pierces","slashes","crushes","scores","bashes","backstabs","kicks","bash","slash","bashes"]

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
		tokens = re.split(r"\] ",line)
		
		#for token in tokens:
		#	print("Token:-" + token)
				
		for name in names:
			#firstWord = tokens[1]
			#print("First word:" + firstWord)
			if len(tokens) > 1 and re.match(name,tokens[1]):
				secondWord = re.split(r" ",tokens[1])[1]
				for word in damageWords:
					if word == secondWord:
						print("Found match: " + tokens[1])
						damage = int(re.findall(r'\d+',tokens[1])[0])
						party[name] += damage
						break
		
	print(party)
	file.close()
	

getTotalDamage("321.txt", "You", "Ayza", "Sylkyn")