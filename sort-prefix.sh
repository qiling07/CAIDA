#!/bin/bash

continents=(NA SA AS EU AF OC)
for continent in "${continents[@]}"
do
	echo ${continent}
	python3 sort-prefix.py ${continent} > raw-data/${continent}.prefix
done
