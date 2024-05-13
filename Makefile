clean_translations_temp_directory:
	rm -rf I18N/

create_virtual_env:
	rm -rf .venv
	python3 -m venv .venv
	# TODO: Publish new version on pypi as `python3-localizable`
	. .venv/bin/activate && pip install openedx-atlas
	. .venv/bin/activate && pip install lxml

pull_translations: clean_translations_temp_directory create_virtual_env
	. .venv/bin/activate && atlas pull $(ATLAS_OPTIONS) translations/openedx-app-android/I18N:I18N
	. .venv/bin/activate && python i18n_scripts/translation_script.py --split
	make clean_translations_temp_directory


extract_translations: clean_translations_temp_directory create_virtual_env
	. .venv/bin/activate && python i18n_scripts/translation_script.py --extract
