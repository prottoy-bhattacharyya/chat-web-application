#create virtual environment
py -3 -m venv .venv

#activate virtual environment
.venv\Scripts\activate

#install dependencies
pip install Flask
pip install mysql-connector-python

#run app
flask --app hello run

#run app with other devices
flask --app hello run --host=0.0.0.0