# Call python script to migrate the database
python src/manage.py db init
python src/manage.py db migrate
python src/manage.py db upgrade