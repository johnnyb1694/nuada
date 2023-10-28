# Nuada

A project dedicated to extracting data from freely available news outlet APIs and storing this data inside a structured format online.

The name 'Nuada' alludes to a famous king in Celtic mythology known for his silver arm. This name symbolizes the process of shaping and molding data.

# Example calls

New York Times: https://api.nytimes.com/svc/archive/v1/2022/9.json?api-key={KEY}
Guardian: https://content.guardianapis.com/search?show-blocks=body&api-key={KEY}&page-size=50&from-date=2022-09-01

The structure is roughly: {protocol}/{domain}/{path}/{resource}/{{params}}

# Design considerations

This tool, ultimately, will need to:

(a) Download data from each aforementioned endpoint; 
(b) Store this data inside a basic relational format

It will need to execute the above tasks on a scheduled basis. The solution will ultimately be deployed to AWS.

We will begin with a simple structure for the application:

-> { nuada }
    -> __init__.py
    -> db.py
    -> resources.py



