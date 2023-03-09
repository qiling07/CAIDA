import json

continents = ["NA", "SA", "AS", "EU", "AF", "OC"]
continents_asn = {"NA":set(), "SA":set(), "AS":set(), "EU":set(), "AF":set(), "OC":set()}
continents_numPrefixes = {"NA":0, "SA":0, "AS":0, "EU":0, "AF":0, "OC":0}
continents_numIPs = {"NA":0, "SA":0, "AS":0, "EU":0, "AF":0, "OC":0}

asInfoFileName = "asns.jsonl"
with open(asInfoFileName, 'r') as asInfoFile :
	for asInfo in asInfoFile :
		asInfo = json.loads(asInfo)
		asn = asInfo['asn']
		continent = asInfo['country']['continent']
		numPrefixes = asInfo['announcing']['numberPrefixes']
		numIPs = asInfo['announcing']['numberAddresses']
		if continent in continents :
			continents_asn[continent].add(asn)
			continents_numPrefixes[continent] += numPrefixes
			continents_numIPs[continent] += numIPs
		else :
			print("error: unknown continent", continent, "for as", asn)

# print sorted asn
# outFileName = "asn_sorted.txt"
# with open(outFileName, 'w') as outFile :
# 	for continent in continents :
# 		asns = continents_asn[continent]
# 		outFile.write(continent)
# 		outFile.write(" ")
# 		for asn in asns :
# 			outFile.write(asn)
# 			outFile.write(" ")
# 		outFile.write("\n")

print("continent", ":", "#asn", "#prefix", "#ip")
for continent in continents :
	print(continent, ":", len(continents_asn[continent]), continents_numPrefixes[continent], continents_numIPs[continent])


