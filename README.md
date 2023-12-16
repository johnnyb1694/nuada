# Nuada

A project dedicated to extracting data from freely available news outlet APIs and mapping reporting trends.

The name 'Nuada' alludes to a famous king in Celtic mythology known for his silver arm. This name symbolizes the process of shaping and molding data into something useful.

# Example calls

New York Times: https://api.nytimes.com/svc/archive/v1/2022/9.json?api-key={KEY}
Guardian: https://content.guardianapis.com/search?show-blocks=body&api-key={KEY}&page-size=50&from-date=2022-09-01

We will begin by simply integrating calls to the New York Times API; starting simply first is always a good approach.

# Design considerations

At the end of this process, a user should be able to select a given 'month' of interest and be presented with the most 'popular' topics of that month.

This means that, on a monthly basis:

-> A call must be issued to the New York Times API to download the required data
-> An algorithm must ingest the required data (from the previous step) and assemble the highest ranking topics from each month
-> The results should, subsequently, be stored inside a relational database

# Setup

To configure the setup for this pipeline, simply run `./setup.sh nuada-archives`



