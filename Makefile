.DEFAULT_GOAL = help

run:
	python manage.py runserver --settings=huestion_project.settings.local

tests:
	python manage.py test --settings=huestion_project.settings.local

unit-tests:
	python manage.py test questions --settings=huestion_project.settings.local
	
functional-tests:
	python manage.py test functional_tests --settings=huestion_project.settings.local

parallel-tests:
	python manage.py test questions --parallel --settings=huestion_project.settings.local

reverse-tests:
	python manage.py test questions --reverse --settings=huestion_project.settings.local

coverage:
	coverage run manage.py test --settings=huestion_project.settings.local
	coverage report

shell:
	python manage.py shell_plus --settings=huestion_project.settings.local

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
	@echo "functional-tests"
	@echo "    Run only the functional tests"
	@echo "parallel-tests"
	@echo "    Run unit tests with parallelization"
	@echo "reverse-tests"
	@echo "    Run test in reverse order"
	@echo "shell"
	@echo "    Run shell_plus"
	@echo ""
	@echo "==Reminders==="
	@echo "How to use black in this project"
	@echo "    black . -l 79 --diff --color -S"
	@echo "How to use isort with Black. Eg:"
	@echo "    isort questions/tests/test_factories.py --diff -m 3 --color"
	@echo "Parallel testing doesn't work on python 3.8 and Django 3.1"
	@echo "    it will be fixed on Django 3.2."
	@echo "    You have to export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES"
	@echo "    and multiprocessing.set_start_method('fork') within the"
	@echo "    manage.py file (this is already done for this project)"
