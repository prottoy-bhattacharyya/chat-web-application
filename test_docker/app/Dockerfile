# FROM ubuntu
FROM nginx 

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y

WORKDIR /app
COPY . /app
# RUN cd /app

RUN pip install -r requirements.txt --break-system-packages

ENTRYPOINT ["python3", "main.py"]
