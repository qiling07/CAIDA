sort-prefix.py: sort prefixes into continents and collect statistics
routeviews.pfx2as: { ip, len, asn}, collect from https://publicdata.caida.org/datasets/routing/routeviews-prefix2as/ on 2023-03-01

sort-asn.py: sort as into continents and collect statistics
asns.jsonl: {asn, geo, #prefix, #ip}, collect from https://api.asrank.caida.org/v2/graphql on 2022-12-01
asn_sorted.txt: {continent: [asns]}, sorted based on asns.jsonl
error.txt: error message for asns.jsonl
stat.txt: statistics for asns.jsonl
