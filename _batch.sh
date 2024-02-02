#!/bin/bash

month_from=$((10#$1))
month_to=$((10#$2))
year=$((10#$3))

for ((month=month_from; month<=month_to; month++)); do
    docker exec -it nuada-pipeline python _pipeline.py --year=$year --month=$month
done
