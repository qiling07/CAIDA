import sys
import json
import os
import random
import ipaddress as ipad

finalChoice = {"NA":ipad.ip_network("7.0.0.0/8"), 
               "SA":ipad.ip_network("177.0.0.0/8"), 
               "OC":ipad.ip_network("203.0.0.0/8"), 
               "EU":ipad.ip_network("53.0.0.0/8"), 
               "AF":ipad.ip_network("41.0.0.0/8"), 
               "CN":ipad.ip_network("183.0.0.0/8"), # CN
               "JP":ipad.ip_network("219.0.0.0/8")  # JP
               }

def dictAdd(d, key, val, country):
    if key in d.keys():
        cInfo = d[key]
        if country in cInfo.keys() :
            cInfo[country] += val
        else :
            cInfo[country] = val
    else:
        d[key] = {country : val}

def SumUp(d) :
    sum = 0
    for key in d.keys() :
        sum += d[key]
    return sum

def printComponents(network, d) :
    print("(", end=" ")
    if len(d) == 0 :
        print("N/A", end="  ")
        print(")", end=" ")
        return

    d = sorted(d.items(), key= lambda item: item[1], reverse=True)
    base = network.num_addresses
    for (cName, ipCnt) in d :
        ratio = 100 * ipCnt / base
        if ratio > 10 :
            print(cName + ":" + "{:.1f}".format(ratio) + "%", end="  ")
    print(")", end=" ")

def asn2Country(d, asn) :
    if asn in d.keys() :
        return d[asn]
    else :
        return "Unknown"

continents_asn = {}
unrecognized_asn = set()

# load sorted asn
asnSortedFileName = "asn-sorted/asn_sorted.txt"
with open(asnSortedFileName, 'r') as asnSortedFile:
    for line in asnSortedFile:
        line = line.rstrip("\n")
        line = line.split()
        asns = set()
        for i in range(1, len(line)):
            asns.add(int(line[i]))
        continents_asn[line[0]] = asns

# filter out prefixes of interest
interest = sys.argv[1]
prefixes = []
totalIP = 0
pfx2asFileName = "raw-data/routeviews-rv2-20230301-1200.pfx2as"
with open(pfx2asFileName, 'r') as fpx2asFile:
    for line in fpx2asFile:
        line = line.rstrip("\n").split()
        ip = line[0]
        length = line[1]
        asn = int(line[2])

        if asn in continents_asn[interest]:
            temp = ipad.ip_network(ip+"/"+length)
            totalIP += temp.num_addresses
            prefixes.append((temp, False, asn))

# locInfo = {asn, countryName}
asInfoFileName = "raw-data/asns.jsonl"
locInfo = {}
with open(asInfoFileName, 'r') as asInfoFile :
    for asInfo in asInfoFile :
        asInfo = json.loads(asInfo)
        asn = int(asInfo['asn'])
        continent = asInfo['country']['continent']
        country = asInfo['country']['name']
        if continent == interest :
            locInfo[asn] = country

targets = []
for i in range(8, 9) :
    curLevel = i
    networks = {}
    for prefix, selected, asn in prefixes:
        if selected :
            continue
        if curLevel < prefix.prefixlen:
            dictAdd(networks, prefix.supernet(new_prefix=curLevel), prefix.num_addresses, asn2Country(locInfo, asn))
        elif curLevel > prefix.prefixlen:
            for subnet in list(prefix.subnets(new_prefix=curLevel)):
                dictAdd(networks, subnet, subnet.num_addresses, asn2Country(locInfo, asn))
        else:
            dictAdd(networks, prefix, prefix.num_addresses, asn2Country(locInfo, asn))
    networks = sorted(networks.items(), key=lambda item: SumUp(item[1]), reverse=True)
    for network, cInfo in networks :
        ratio = SumUp(cInfo) / network.num_addresses
        if network == finalChoice[interest] :
            targets.append((network, cInfo))
            for i in range(len(prefixes)) :
                prefix = prefixes[i][0]
                selected = prefixes[i][1]
                asn = prefixes[i][2]
                if not selected and network.supernet_of(prefix) :
                    prefixes[i] = (prefix, True, asn)
            break

subtargets = {}
for i in range(12, 13) :
    curLevel = i
    for prefix, selected, asn in prefixes:
        if not selected :
            continue
        if curLevel < prefix.prefixlen:
            dictAdd(subtargets, prefix.supernet(new_prefix=curLevel), prefix.num_addresses, locInfo[asn])
        elif curLevel > prefix.prefixlen:
            for subnet in list(prefix.subnets(new_prefix=curLevel)):
                dictAdd(subtargets, subnet, subnet.num_addresses, locInfo[asn])
        else:
            dictAdd(subtargets, prefix, prefix.num_addresses, locInfo[asn])


def printRaw() :
    print("continent:", interest, "\tnum_prefiex:", len(prefixes), "\tnum_ip", totalIP)
    print("network" + "\t" + "usefulRatioPer(%)" + "\t" + "totalProbe" + "\t" + "coverage(%)")
    totalProbe = 0
    for network, cInfo in targets :
        ipCnt = SumUp(cInfo)
        totalProbe = network.num_addresses
        ratio = ipCnt / network.num_addresses
        print(interest+ "\t" + str(network) + "\t" + "{:.2f}".format(100*ratio) + "%\t" + str(totalProbe) + "\t" + "{:.2f}".format(100*ipCnt/totalIP) + "%", end="\t")
        printComponents(network, cInfo)
        print()
        for subtarget in list(network.subnets(new_prefix=12)) :
            subIpCnt = 0
            subCInfo = {}
            if subtarget in subtargets.keys() :
                subIpCnt = SumUp(subtargets[subtarget])
                subCInfo = subtargets[subtarget]
            print("\t\t" + str(subtarget) + "\t" + "{:.2f}".format(100 * subIpCnt / subtarget.num_addresses) + "%", end="\t")
            printComponents(subtarget, subCInfo)
            print()
printRaw()

## N=12 is a good approx for most continents except for OC
def printByN(N) :
    targetsN = []
    cumulated = 0
    totalProbe = 0
    for network, ipCnt in targets :
        if network.prefixlen <= N :
            for temp in list(network.subnets(new_prefix=N)) :
                targetsN.append((temp, network))
            cumulated += ipCnt
            totalProbe += network.num_addresses
    targetsN = sorted(targetsN, key=lambda item: item[0].network_address)
    print("#continent:", interest, "\tnum_prefiex:", len(prefixes), "\tnum_ip", totalIP)
    print("#chosen:" + "\tnum_prefix_N:" + str(len(targetsN)) + "\tuseful_num_ip:" + str(cumulated) + "\t" + "\tnum_ip:" + str(totalProbe))
    for target, father in targetsN :
        print(str(target) + "\t" + str(father))
# if interest == "OC" :
#     printByN(14)
# else :
#     printByN(12)

## generate directories and subnets(16)
def printBy16(N, parent_dir) :
    file12 = open(os.path.join(parent_dir, "12.prefixes"), "w")
    targetsN = []
    for network, cInfo in targets :
        if network.prefixlen <= N :
            for temp in list(network.subnets(new_prefix=N)) :
                targetsN.append((temp, network))
    # random.shuffle(targetsN)
    for target, father in targetsN :
        file12.write(str(target) + "\n")
        directory = os.path.join(parent_dir, str(target).replace("/", "_"))
        os.mkdir(directory)
        file16 = open(os.path.join(directory, "16.prefixes"), "w")
        temp = list(target.subnets(new_prefix=16))
        random.shuffle(temp)
        for net16 in temp :
            file16.write(str(net16) + "\n")
        file16.close()
    file12.close()

directory = interest
parent_dir = "/home/ubuntu/CAIDA/results/"
parent_dir = os.path.join(parent_dir, directory)
os.mkdir(path=parent_dir)
printBy16(12, parent_dir)

# if interest == "OC" :
#     printBy16(14, parent_dir)
# else :
#     printBy16(12, parent_dir)



