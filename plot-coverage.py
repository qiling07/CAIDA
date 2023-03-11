import matplotlib.pyplot as plt

continents = ["NA", "SA", "AS", "EU", "AF", "OC"]

datas = {}
coverageFileName = "prefixes-distribution/coverage.continents"
with open(coverageFileName, 'r') as file :
    for line in file :
        line = line.rstrip("\n")
        line = line.split()
        continent = line[0]
        datas[continent] = []
        for i in range(1, len(line)) :
            datas[continent].append(float(line[i]))


for continent in datas.keys() :
    data = datas[continent]
    plt.plot(list(range(0, len(data))), data, label=continent)

plt.xlabel("prefixLen")
plt.ylabel("coverage(%)")
plt.legend()
plt.savefig("coverage-continents.png")