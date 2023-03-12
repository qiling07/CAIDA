import sys
import os
import random
import ipaddress as ipad


def dictAdd(d, key, val):
    if key in d.keys():
        d[key] = d[key] + val
    else:
        d[key] = val


continents = ["NA", "SA", "AS", "EU", "AF", "OC"]
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
            asns.add(line[i])
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
        asn = line[2]

        if asn in continents_asn[interest]:
            temp = ipad.ip_network(ip+"/"+length)
            totalIP += temp.num_addresses
            prefixes.append((temp, False))

targets = []
for i in range(8, 9) :
    curLevel = i
    networks = {}
    for prefix, selected in prefixes:
        if selected :
            continue
        if curLevel < prefix.prefixlen:
            dictAdd(networks, prefix.supernet(new_prefix=curLevel), prefix.num_addresses)
        elif curLevel > prefix.prefixlen:
            for subnet in list(prefix.subnets(new_prefix=curLevel)):
                dictAdd(networks, subnet, subnet.num_addresses)
        else:
            dictAdd(networks, prefix, prefix.num_addresses)
    networks = sorted(networks.items(), key=lambda item: item[1], reverse=True)
    for network, ipCnt in networks :
        ratio = ipCnt / network.num_addresses
        if ratio > 0.7 or (ratio > 0.2 and interest == "OC") :
            targets.append((network, ipCnt))
            for i in range(len(prefixes)) :
                prefix = prefixes[i][0]
                selected = prefixes[i][1]
                if not selected and network.supernet_of(prefix) :
                    prefixes[i] = (prefix, True)
        else :
            break

subtargets = {}
for i in range(12, 13) :
    curLevel = i
    for prefix, selected in prefixes:
        if not selected :
            continue
        if curLevel < prefix.prefixlen:
            dictAdd(subtargets, prefix.supernet(new_prefix=curLevel), prefix.num_addresses)
        elif curLevel > prefix.prefixlen:
            for subnet in list(prefix.subnets(new_prefix=curLevel)):
                dictAdd(subtargets, subnet, subnet.num_addresses)
        else:
            dictAdd(subtargets, prefix, prefix.num_addresses)


# print("network" + "\t" + "usefulRatioPer(%)" + "\t" + "totalProbe(%)" + "\t" + "coverage(%)")
def printRaw() :
    # print("continent:", interest, "\tnum_prefiex:", len(prefixes), "\tnum_ip", totalIP)
    cumulated = 0
    totalProbe = 0
    for network, ipCnt in targets :
        cumulated = ipCnt
        totalProbe = network.num_addresses
        ratio = ipCnt / network.num_addresses
        print(interest+ "\t" + str(network) + "\t" + "{:.2f}".format(100*ratio) + "%\t" + str(totalProbe) + "\t" + "{:.2f}".format(100*cumulated/totalIP) + "%")
        for subtarget in list(network.subnets(new_prefix=12)) :
            subIpCnt = 0
            if subtarget in subtargets.keys() :
                subIpCnt = subtargets[subtarget]
            print("\t\t" + str(subtarget) + "\t" + "{:.2f}".format(100 * subIpCnt / subtarget.num_addresses) + "%")
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
    cumulated = 0
    totalProbe = 0
    for network, ipCnt in targets :
        if network.prefixlen <= N :
            for temp in list(network.subnets(new_prefix=N)) :
                targetsN.append((temp, network))
            cumulated += ipCnt
            totalProbe += network.num_addresses
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

# directory = interest
# parent_dir = "/home/ubuntu/CAIDA/results/"
# parent_dir = os.path.join(parent_dir, directory)
# os.mkdir(path=parent_dir)
# printBy16(12, parent_dir)

# if interest == "OC" :
#     printBy16(14, parent_dir)
# else :
#     printBy16(12, parent_dir)



