for month in {1..12}; do
    docker exec -it nuada-pipeline python _pipeline.py --year=2023 --month=$month
done