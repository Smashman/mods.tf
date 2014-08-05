# mods.tf

The website source for mods.tf, powered by Flask - currently in the development stages

## Requirements

* Bower
* Sass
* vpk_linux32

## Set-up

* ```pip install -r requirements.txt```
* ```bower install```
* Set-up ```instance/settings.py``` based on ```instance/settings_example.py``` template.
* ```alembic upgrade head```
* ```python manage.py update_tf2_items```
* ```python manage.py runserver```

## License

Copyright &copy; 2014 Ben Williams

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A copy of the GNU General Public License can be found at http://www.gnu.org/licenses/.

For your convenience, a copy of this license is included.