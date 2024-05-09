# EducationX Android

Modern vision of the mobile application for the Open EdX platform from Raccoon Gang.

[Documentation](Documentation/Documentation.md)

## Building

1. Check out the source code:

        git clone https://github.com/openedx/openedx-app-android.git

2. Open Android Studio and choose Open an Existing Android Studio Project.

3. Choose ``openedx-app-android``.

4. Configure the [config.yaml](default_config/dev/config.yaml) with URLs and OAuth credentials for your Open edX instance.

5. Select the build variant ``develop``, ``stage``, or ``prod``.

6. Click the **Run** button.

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

## API plugin

This project uses custom APIs to improve performance and reduce the number of requests to the server.

You can find the plugin with the API and installation guide [here](https://github.com/raccoongang/mobile-api-extensions).

## License

The code in this repository is licensed under the Apache-2.0 license unless otherwise noted.

Please see [LICENSE](https://github.com/openedx/openedx-app-android/blob/main/LICENSE) file for details.
