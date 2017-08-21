def getTotalDamage (filename, *names):
	file = open(filename)
	print("Opened file: " + filename)
	party = {}
	for name in names:
		party[name] = 0
	#for lines in file:
		
		
	print(party)
	file.close()
	

	
getTotalDamage("C:\EverQuest\Logs\eqlog_Solicer_project1999.txt", "Aegaeon", "Dsturbed", "Leftears")
