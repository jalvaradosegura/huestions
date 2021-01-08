.DEFAULT_GOAL = help

run:
	python manage.py runserver

tests:
	python manage.py test

unit-tests:
	python manage.py test questions

parallel-tests:
	python manage.py test questions --parallel

coverage:
	coverage run manage.py test
	coverage report

help:
	@echo "==Commands==="
	@echo "run"
	@echo "    Run Django project"
	@echo "tests"
	@echo "    Run all the tests"
	@echo "coverage"
	@echo "    Run coverage + report"
	@echo ""
	@echo "==Reminders==="
	@echo "How to use black in this project"
	@echo "    black . -l 79 --diff --color -S"
	@echo "Parallel testing doesn't work on python 3.8 and Django 3.1"
	@echo "it will be fixed on Django 3.2"
