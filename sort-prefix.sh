#!/bin/bash

continents=(NA SA AS EU AF OC)
for continent in "${continents[@]}"
do
	echo ${continent}
	python3 sort-prefix.py ${continent} > prefixes-sorted/${continent}-leq-16-mod.prefix
done
