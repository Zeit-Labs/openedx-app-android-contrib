"""
# Translation Management Script

This script is designed to manage translations for a project by performing two operations:
1) Extracting English translations from all modules.
2) Splitting translations into separate files for each module and language into a single file.

## Usage

```bash
python translation.py --extract

or

python translation.py --split

"""
import argparse
import os
from lxml import etree


def parse_arguments():
    """
    This function is the argument parser for this script.
    The script takes only one of the two arguments --split or --extract as indicated below.
    """
    parser = argparse.ArgumentParser(description='Split or extract translations.')
    parser.add_argument('--split', action='store_true',
                        help='Split translations into separate files for each module and language.')
    parser.add_argument('--extract', action='store_true',
                        help='Extract the English translations from all modules into a single file.')
    return parser.parse_args()


def append_element_and_comment(element, previous_element, root):
    """
    Appends the given element to the root XML element, preserving the previous element's comment if exists.

    Args:
        element (etree.Element): The XML element to append.
        previous_element (etree.Element or None): The previous XML element before the current one.
        root (etree.Element): The root XML element to append the new element to.

    Returns:
        None
    """
    # If there was a comment before the current element, add it first.
    if isinstance(previous_element, etree._Comment):
        previous_element.tail = '\n\t'
        root.append(previous_element)

    # Indent all elements with one tab.
    element.tail = '\n\t'
    root.append(element)


def get_translation_file_path(modules_dir, module):
    """
    Retrieves the path of the translation file from the module name

    Parameters:
        modules_dir (str): The path to the directory containing all the modules.
        module (str): The module's name that we want its translation.

    Returns:
        file_path (str): The module's translation path.
    """
    translation_file = os.path.join(modules_dir, module, 'src', 'main', 'res', 'values', 'strings.xml')
    return translation_file


def write_translation_file(modules_dir, root, module, lang_dir):
    """
    Writes the XML root element to a strings.xml file in the specified language directory.

    Args:
        modules_dir (str): The root directory of the project.
        root (etree.Element): The root XML element to be written.
        module (str): The name of the module.
        lang_dir (str): The language directory to write the XML file to.

    Returns:
        None
    """
    combined_translation_dir = os.path.join(modules_dir, module, 'src', 'main', 'res', lang_dir)
    os.makedirs(combined_translation_dir, exist_ok=True)

    tree = etree.ElementTree(root)
    tree.write(os.path.join(combined_translation_dir, 'strings.xml'), encoding='utf-8', xml_declaration=True)


def get_modules_to_translate(modules_dir):
    """
    Retrieves a list of modules to be translated from the specified directory (Project directory).

    Args:
        modules_dir (str): The directory containing the modules.

    Returns:
        list of str: A list of module names.
    """
    # Get all directories within the modules directory except for 'i18n'
    dirs = [
        directory for directory in os.listdir(modules_dir)
        if os.path.isdir(os.path.join(modules_dir, directory)) and directory != 'i18n'
    ]

    modules_list = []
    # Check each directory for a translation file and add it to the list if found
    for module in dirs:
        translation_file = get_translation_file_path(modules_dir, module)
        if os.path.isfile(translation_file):
            modules_list.append(module)
    return modules_list


def process_module_translations(root, combined_root, module):
    """
    Process translations from a module and append them to the combined translations.

    Parameters:
        root (etree.Element): The root element of the module translations.
        combined_root (etree.Element): The combined translations root element.
        module (str): The name of the module.

    Returns:
        etree.Element: The updated combined translations root element.
    """
    previous_element = None
    for element in root.getchildren():
        translatable = element.attrib.get('translatable', True)
        if (
                translatable and translatable != 'false'  # Check for the translatable property.
                and element.tag in ['string', 'string-array', 'plurals']  # Only those types are read by transifex.
                and (not element.nsmap
                     or element.nsmap and not element.attrib.get('{%s}ignore' % element.nsmap["tools"]))
        ):
            element.attrib['name'] = '.'.join([module, element.attrib.get('name')])

            append_element_and_comment(element, previous_element, combined_root)

        # To check for comments in the next round.
        previous_element = element

    return combined_root


def combine_translations(modules_dir):
    """
    Combine translations from all specified modules into a single XML element.

    Parameters:
        modules_dir (str): The directory containing the modules.

    Returns:
        etree.Element: An XML element representing the combined translations.
    """
    combined_root = etree.Element('resources')
    combined_root.text = '\n\t'

    modules = get_modules_to_translate(modules_dir)
    for module in modules:
        translation_file = get_translation_file_path(modules_dir, module)
        module_translations_tree = etree.parse(translation_file)
        root = module_translations_tree.getroot()
        combined_root = process_module_translations(root, combined_root, module)

        # Put a new line after each module translations.
        if len(combined_root):
            combined_root[-1].tail = '\n\n\t'

    # Unindent the resources closing tag.
    combined_root[-1].tail = '\n'
    return combined_root


def combine_translation_files(modules_dir=None):
    """
    Combine translation files from different modules into a single file.
    """
    if not modules_dir:
        modules_dir = os.path.dirname(os.path.dirname(__file__))
    combined_root_element = combine_translations(modules_dir)
    write_translation_file(modules_dir, combined_root_element, 'i18n', 'values')


def get_languages_dirs(modules_dir):
    """
    Retrieve directories containing language files for translation.

    Args:
        modules_dir (str): The directory containing all the modules.

    Returns:
        list: A list of directories containing language files for translation. Each directory represents
              a specific language and starts with the 'values-' extension.

    Example:
        Input:
            get_languages_dirs('/path/to/modules')
        Output:
            ['values-ar', 'values-uk', ...]
    """
    lang_parent_dir = os.path.join(modules_dir, 'i18n', 'src', 'main', 'res')
    languages_dirs = [
        directory for directory in os.listdir(lang_parent_dir)
        if (
                directory.startswith('values-')
                and 'strings.xml' in os.listdir(os.path.join(lang_parent_dir, directory))
        )
    ]
    return languages_dirs


def separate_translation_to_modules(modules_dir, lang_dir):
    """
    Separates translations from a translation file into modules.

    Args:
        modules_dir (str): The directory containing all the modules.
        lang_dir (str): The directory containing the translation file being split.

    Returns:
        dict: A dictionary containing the translations separated by module.
        {
            'module_1_name': etree.Element('resources')_1.
            'module_2_name': etree.Element('resources')_2.
            ...
        }
    """
    translations_roots = {}
    # Parse the translation file
    file_path = os.path.join(modules_dir, 'i18n', 'src', 'main', 'res', lang_dir, 'strings.xml')
    module_translations_tree = etree.parse(file_path)
    root = module_translations_tree.getroot()
    previous_entry = None
    # Iterate through translation entries
    for translation_entry in root.getchildren():
        if not isinstance(translation_entry, etree._Comment):
            # Split the key to extract the module name
            module_name, key_remainder = translation_entry.attrib['name'].split('.', maxsplit=1)
            translation_entry.attrib['name'] = key_remainder

            # Create a dictionary entry for the module if it doesn't exist
            if module_name not in translations_roots:
                translations_roots[module_name] = etree.Element('resources')
                translations_roots[module_name].text = '\n\t'

            # Append the translation entry to the corresponding module
            append_element_and_comment(translation_entry, previous_entry, translations_roots[module_name])

        previous_entry = translation_entry
    return translations_roots


def split_translation_files(modules_dir=None):
    """
    Splits translation files into separate files for each module and language.

    Args:
        modules_dir (str, optional): The directory containing all the modules. Defaults to None.

    """
    # Set the modules directory if not provided
    if not modules_dir:
        modules_dir = os.path.dirname(os.path.dirname(__file__))

    # Get the directories containing language files
    languages_dirs = get_languages_dirs(modules_dir)

    # Iterate through each language directory
    for lang_dir in languages_dirs:
        # Separate translations into modules
        translations = separate_translation_to_modules(modules_dir, lang_dir)
        # Iterate through each module and write its translations to a file
        for module, root in translations.items():
            # Unindent the resources closing tag
            root[-1].tail = '\n'
            # Write the translation file for the module and language
            write_translation_file(modules_dir, root, module, lang_dir)


def main():
    args = parse_arguments()
    if args.split and args.extract:
        print("You can specify either --split or --extract.")
    elif args.split:
        # Call the function to split translations
        split_translation_files()
    elif args.extract:
        # Call the function to extract translations
        combine_translation_files()
    else:
        print("Please specify either --split or --extract.")


if __name__ == "__main__":
    main()
