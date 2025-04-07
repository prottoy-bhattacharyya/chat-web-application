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
flask --app maiin run --host=0.0.0.0