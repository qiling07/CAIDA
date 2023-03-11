import sys
import ipaddress as ipad

def dictAdd(d, key, val) :
    if key in d.keys() :
        d[key] = d[key] + val
    else :
        d[key] = val

continents = ["NA", "SA", "AS", "EU", "AF", "OC"]
continents_asn = {}
unrecognized_asn = set()

asnSortedFileName = "asn-sorted/asn_sorted.txt"
with open(asnSortedFileName, 'r') as asnSortedFile:
    for line in asnSortedFile:
        line = line.rstrip("\n")
        line = line.split()
        asns = set()
        for i in range(1, len(line)):
            asns.add(line[i])
        continents_asn[line[0]] = asns
    
interest = sys.argv[1]
prefixes = []
totalIP = 0

pfx2asFileName = "raw-data/routeviews-rv2-20230301-1200.pfx2as"
with open(pfx2asFileName, 'r') as fpx2asFile:
    for line in fpx2asFile :
        line = line.rstrip("\n").split()
        ip = line[0]
        length = line[1]
        asn = line[2]
        
        if asn in continents_asn[interest] :
            temp = ipad.ip_network(ip+"/"+length)
            totalIP += temp.num_addresses
            prefixes.append(temp)

# print("continent:", interest, "\tnum_prefiex:", len(prefixes), "\tnum_ip", totalIP)
print(interest, end=" ")
for i in range(0, 17) :
    curLevel = i
    networks = {}
    for prefix in prefixes :
        if curLevel < prefix.prefixlen :
            dictAdd(networks, prefix.supernet(new_prefix=curLevel), prefix.num_addresses)
        elif curLevel > prefix.prefixlen :
            for subnet in list(prefix.subnets(new_prefix=curLevel)):
                dictAdd(networks, subnet, subnet.num_addresses)
        else :
            dictAdd(networks, prefix, prefix.num_addresses)
    networks = sorted(networks.items(), key=lambda item: item[1], reverse=True)
    print("{:.2f}".format(100 * networks[0][1]/totalIP), end=" ")
    # print("prefix_len:", curLevel, "num_addresses_per_network:", str(2**(32-curLevel)), "totalIpContinent:", str(totalIP))
    # print("network" + "\t" + "goodIp/network(%)" + "\t" + "goodIp/totalIp(%)" + "\t" + "cumulatedGoodIp(%)")
    # cumulated = 0
    # for i in range(len(networks)) :
    #     cumulated += 100 * networks[i][1] / totalIP
    #     print(str(networks[i][0]) + "\t" + "{:.2f}".format(100 * networks[i][1] / networks[i][0].num_addresses) + "\t" + "{:.2f}".format(100 * networks[i][1] / totalIP) + "\t" + str(int(cumulated)))
    # print()
print()
