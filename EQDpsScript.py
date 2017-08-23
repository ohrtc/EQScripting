import re

def getTotalDamage (filename, *names):
	file = open(filename)
	print("Opened file: " + filename)
	party = {}
	for name in names:
		party[name] = 0
	for line in file:
		#print(line)
		#tokens = line.split(r'(:.*:)')#(\[.*\])
		regObj = re.compile(r"(\[.*\])")
		tokens = regObj.split(line)
		for token in tokens:
			print("Token:-" + token)
		#for token in tokens:
		#	print(token)
		
	##print(party)
	file.close()
	

getTotalDamage("C:\\Users\Cam\Documents\GitHub\EQScripting\eqlog_Solicer_project1999.txt", "Aegaeon", "Dsturbed", "Leftears")
