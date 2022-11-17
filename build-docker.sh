docker build -t weygu/siwi-api:0.3 .
docker build -t weygu/siwi-api:latest .
docker login --username weygu
docker push -a weygu/siwi-api
