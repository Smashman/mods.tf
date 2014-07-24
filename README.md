# mods.tf

The website source for mods.tf, powered by Flask - currently in the development stages

## Requirements

* Bower
* Sass

## Set-up

* ```pip install -r requirements.txt```
* ```bower install```
* Set-up ```instance/settings.py``` based on ```instance/settings_example.py``` template.
* ```alembic upgrade head```
* ```python manage.py update_tf2_items```
* ```python manage.py runserver```