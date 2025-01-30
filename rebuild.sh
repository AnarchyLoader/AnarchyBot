docker build --tag=anarchybob/sigma .
docker kill anarchybob
docker rm anarchybob
docker run -d --name anarchybob anarchybob/sigma