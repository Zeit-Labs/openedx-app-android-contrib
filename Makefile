clean_translations_temp_directory:
	rm -rf i18n/

translation_requirements:
	pip install -r i18n_scripts/requirements.txt

pull_translations: clean_translations_temp_directory
	atlas pull $(ATLAS_OPTIONS) translations/openedx-app-android/i18n:i18n
	python i18n_scripts/translation_script.py --split

extract_translations: clean_translations_temp_directory
	python i18n_scripts/translation_script.py --extract
