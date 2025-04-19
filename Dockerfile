FROM ubuntu

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install python3 -y
RUN pip install --requirement requirements.txt

COPY . .

ENTRYPOINT [ "python3" , "main.py" ]