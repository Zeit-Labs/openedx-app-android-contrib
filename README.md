# Open edX Android

Modern vision of the mobile application for the Open edX platform from Raccoon Gang.

[Documentation](Documentation/Documentation.md)

## Building

1. Check out the source code:

        git clone https://github.com/openedx/openedx-app-android.git

2. Open Android Studio and choose Open an Existing Android Studio Project.

3. Choose ``openedx-app-android``.

4. Configure `config_settings.yaml` inside `default_config` and `config.yaml` inside sub directories to point to your Open edX configuration. [Configuration Documentation](./Documentation/ConfigurationManagement.md)

5. Select the build variant ``develop``, ``stage``, or ``prod``.

6. Click the **Run** button.

## API
This project targets on the latest Open edX release and rely on the relevant mobile APIs.

If your platform version is older than December 2023, please follow the instructions to use the [API Plugin](./Documentation/APIs_Compatibility.md).

## Translation
### How it works for the developer.
- For a developer to translate the App, he/she should, in a normal case,  run `make pull_translations` in terminal. This command will do the following:
   1. Pull the translations from [openedx translations](https://github.com/openedx/openedx-translations), where the app source translations to the supported languages are.
   2. Split those translations each entry to its corresponding module. 
   3. Remove the pulled files.
   
  then the app would have been translated.

- Now, in the ***testing*** phase, the translations are in `Zeit-Labs/openedx-translations` repo under `fc_55_sample` branch and the tester should use the below command to test:
    ```
  make ATLAS_OPTIONS='--repository=Zeit-Labs/openedx-translations --branch=fc_55_sample' pull_translations
  ```
### How it works for the translator.
- After a new push to the 'develop' branch, an automated action will do the following:
  1. Run `make extract_translations` which will extract the translation entries from the app modules to the single file `I18N/en.lproj/Localization.strings`.
  2. Push that file to [openedx translations](https://github.com/openedx/openedx-translations) to be translated later by translators.

- As a side note, the automated github action has not been writen yet.

## License

The code in this repository is licensed under the Apache-2.0 license unless otherwise noted.

Please see [LICENSE](https://github.com/openedx/openedx-app-android/blob/main/LICENSE) file for details.
