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
	@echo "unit-tests"
	@echo "    Run only the unit tests"
	@echo "parallel-tests"
	@echo "    Run unit tests with parallelization"
	@echo ""
	@echo "==Reminders==="
	@echo "How to use black in this project"
	@echo "    black . -l 79 --diff --color -S"
	@echo "Parallel testing doesn't work on python 3.8 and Django 3.1"
	@echo "    it will be fixed on Django 3.2."
	@echo "    You have to export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES"
	@echo "    and multiprocessing.set_start_method('fork') within the"
	@echo "    manage.py file (this is already done for this project)"
