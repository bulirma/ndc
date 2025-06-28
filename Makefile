.PHONY: localize localization-update run count-python-sloc

messages.pot: babel.cfg
	pybabel extract -F babel.cfg -o messages.pot .

translations/en: messages.pot
	pybabel init -i messages.pot -d translations -l en
	
translations/cs: messages.pot
	pybabel init -i messages.pot -d translations -l cs

translations/el: messages.pot
	pybabel init -i messages.pot -d translations -l el

localization-update: messages.pot
	pybabel update -i messages.pot -d translations

localize:
	pybabel compile -d translations

run:
	flask run --debug

count-python-sloc:
	@sh scripts/count-python-sloc.sh
