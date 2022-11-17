docker build -t weygu/siwi-api:0.3.3 .
docker login --username weygu
docker push -a weygu/siwi-api
