
continents = ["NA", "SA", "AS", "EU", "AF", "OC"]
continents_asn = {}
continents_numPrefixes = {"NA":0, "SA":0, "AS":0, "EU":0, "AF":0, "OC":0}
unrecognized_asn = set()

asnSortedFileName = "asn_sorted.txt"
with open(asnSortedFileName, 'r') as asnSortedFile:
    for line in asnSortedFile:
        line = line.rstrip("\n")
        line = line.split()
        asns = set()
        for i in range(1, len(line)):
            asns.add(line[i])
        continents_asn[line[0]] = asns

pfx2asFileName = "routeviews-rv2-20230301-1200.pfx2as"
with open(pfx2asFileName, 'r') as fpx2asFile:
    for line in fpx2asFile :
        line = line.rstrip("\n").split()
        ip = line[0]
        len = line[1]
        asn = line[2].split('_')[0]
        asn = asn.split(',')[0]
        continent = ""

        for temp in continents :
            if asn in continents_asn[temp] :
                continent = temp
                break
        
        if continent :
            continents_numPrefixes[continent] += 1
        else :
            unrecognized_asn.add(asn)

print("error unrecognized asn:", unrecognized_asn)
print(continents_numPrefixes)
