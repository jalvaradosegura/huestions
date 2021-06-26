![Coveralls](https://img.shields.io/coveralls/github/jalvaradosegura/huestions?style=for-the-badge)
![Code style](https://img.shields.io/badge/code%20style-black-black?style=for-the-badge)
![Imports](https://img.shields.io/badge/imports-isort-orange?style=for-the-badge)
[![GitHub license](https://img.shields.io/github/license/jalvaradosegura/huestions?color=blue&style=for-the-badge)](https://github.com/jalvaradosegura/huestions/blob/main/LICENSE)


# Huestions 🦥
Answer & Create lists of hard questions
<img src="https://i.imgur.com/eg0OmBU.png" alt="403">

## How to run the project locally
```sh
# Install the dependencies
pipenv install

# Go into your virtual environment
pipenv shell

# Apply migrations and create a Demo List. Do one of the following options.
# Option 1:
make set-up-local-environment
# Option 2
python manage.py migrate --settings=huestion_project.settings.local
python manage.py create_demo_list --settings=huestion_project.settings.local

# Run the project. Again 2 options.
# Option 1:
make run
# Option 2:
python manage.py runserver --settings=huestion_project.settings.local
```

The website will be running at: http://localhost:8000/

## Cool stuff
### It has a main character
<img src="https://github.com/jalvaradosegura/huestions/blob/main/static/images/huesty_thanks.png" alt="thanks" width="200" height="278">
<img src="https://github.com/jalvaradosegura/huestions/blob/main/static/images/huesty.png" alt="register" width="200" height="300">

### Custom error views
<img src="https://raw.githubusercontent.com/jalvaradosegura/huestions/main/static/images/404.png" alt="404">
<img src="https://raw.githubusercontent.com/jalvaradosegura/huestions/main/static/images/500.png" alt="500">
<img src="https://raw.githubusercontent.com/jalvaradosegura/huestions/main/static/images/403.png" alt="403">

