#!/bin/bash

# continents=(NA SA AS EU AF OC)
continents=(NA SA EU AF OC)
for continent in "${continents[@]}"
do
	echo ${continent}
	# python3 sort-prefix.py ${continent} > raw-data/${continent}.prefix
	# python3 distribution-prefix.py ${continent} >> prefixes-distribution/coverage.continents
	# python3 select-prefix.py ${continent} > prefixes-selected/${continent}.prefix.raw &
	# python3 select-prefix.py ${continent}
	# python3 final-select-prefix.py ${continent} > prefixes-selected/${continent}.prefix.eight
	python3 print-results.py ${continent} >> results/overview.prefixes
done
