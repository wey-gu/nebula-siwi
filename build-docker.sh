docker build -t weygu/siwi-api:0.3.1 .
docker login --username weygu
docker push -a weygu/siwi-api
