# mods.tf

The website source for mods.tf, powered by Flask - currently in the development stages

## Requirements

* Bower
* Sass

## Set-up

* ```pip install -r requirements.txt```
* ```bower install```
* Set-up ```instance/settings.py``` based on ```instance/settings_example.py``` template.
* ```python```
    * ```>>> from app import db```
    * ```>>> db.create_all()```
* ```run.py```