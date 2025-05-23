#create virtual environment
py -3 -m venv .venv

#activate virtual environment for windows
.venv\Scripts\activate
#activate virtual environment for linux
source .venv/bin/activate

#add requirements to txt file
pip freeze > requirements.txt

#install dependencies
pip install --requirement requirements.txt

#run app
flask --app main run

#run app with other devices
flask --app main run --host=0.0.0.0

#build mysql docker
docker build -t chat-app-db .

#run mysql docker
docker run --name mysql-db -e MYSQL_ROOT_PASSWORD=1234 -p 3333:3306 -d chat-app-db

#run main docker
docker run -it -p 3333:3306 -p 5000:5000 test_docker


#test docker
docker build -t mysql-app .
docker build -t flask-app-nginx .
docker network create app-network 
docker run --name mysql-app -e MYSQL_ROOT_PASSWORD=1234 -d -p 3333:3306 mysql
docker run -p 80:80 -p 5000:5000 --network app-network --name flask-app-nginx -d flask-app-nginx



