py -3 -m venv .venv
.venv\Scripts\activate

pip install Flask
pip install mysql-connector-python

flask --app hello run --host=0.0.0.0
