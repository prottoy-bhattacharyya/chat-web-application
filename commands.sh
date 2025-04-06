#create virtual environment
py -3 -m venv .venv

#activate virtual environment for windows
.venv\Scripts\activate
#activate virtual environment for linux
source .venv/bin/activate

#install dependencies
pip install --requirement requirements.txt

#run app
flask --app hello run

#run app with other devices
flask --app hello run --host=0.0.0.0