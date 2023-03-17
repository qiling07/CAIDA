import json
import ipaddress as ipad


pfx2asFileName = "raw-data/routeviews-rv2-20230301-1200.pfx2as"
with open(pfx2asFileName, 'r') as fpx2asFile:
    for line in fpx2asFile :
        line = line.rstrip("\n").split()
        ip = line[0]
        len = line[1]
        asn = line[2]
        if ipad.ip_address("47.88.46.116") in ipad.ip_network(ip + "/" + len) :
            print(ip, len, asn)

exit

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


