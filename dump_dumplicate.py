import sys
import ipaddress as ipad

prefixes = []
totalIP = 0

pfx2asFileName = "raw-data/routeviews-rv2-20230301-1200.pfx2as.raw.duplicated"
with open(pfx2asFileName, 'r') as fpx2asFile:
    for line in fpx2asFile :
        line = line.rstrip("\n").split()
        ip = line[0]
        length = line[1]
        asn = line[2].split('_')[0]
        asn = asn.split(',')[0]
        continent = ""

        temp = ipad.ip_network(ip+"/"+length)
        prefixes.append((temp, asn))

prefixes = sorted(prefixes, key=lambda item : item[0].network_address)

prev = prefixes[0]
out = [prev]
for i in range(1, len(prefixes)) :
    cur = prefixes[i]
    if cur[0].subnet_of(prev[0]) :
        continue
    elif cur[0].supernet_of(prev[0]) :
        print("error")
    else :
        prev = cur
        out.append(cur)

for item in out :
    prefix = item[0]
    print(str(prefix.network_address) + "\t" + str(prefix.prefixlen) + "\t" + item[1])

