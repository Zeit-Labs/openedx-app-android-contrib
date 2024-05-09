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


def get_modules_to_translate(modules_dir):
    """
    Retrieve the names of modules that have translation files for a specified language.

    Parameters:
        modules_dir (str): The path to the directory containing all the modules.

    Returns:
        list of str: A list of module names that have translation files for the specified language.
    """
    dirs = [
        directory for directory in os.listdir(modules_dir)
        if os.path.isdir(os.path.join(modules_dir, directory)) and directory != 'I18N'
    ]

    modules_list = []
    for module in dirs:
        translation_file = get_translation_file_path(modules_dir, module)
        if os.path.isfile(translation_file):
            modules_list.append(module)
    return modules_list


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


def append_element_and_comment(element, previous_element, root):
    # If there was a comment before the current element add it first.
    if isinstance(previous_element, etree._Comment):
        previous_element.tail = '\n\t'
        root.append(previous_element)

    # Indent all elements with on tab.
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
    # lang_dir = '-'.join(['values', lang]) if lang else 'values'
    combined_translation_dir = os.path.join(modules_dir, module, 'src', 'main', 'res', lang_dir)
    os.makedirs(combined_translation_dir, exist_ok=True)

    tree = etree.ElementTree(root)
    tree.write(os.path.join(combined_translation_dir, 'strings.xml'), encoding='utf-8', xml_declaration=True)


def combine_translation_files(modules_dir=None):
    """
    Combine translation files from different modules into a single file.
    """
    if not modules_dir:
        modules_dir = os.path.dirname(os.path.dirname(__file__))
    combined_root_element = combine_translations(modules_dir)
    write_translation_file(modules_dir, combined_root_element, 'I18N', 'values')


def get_languages_dirs(modules_dir):
    """
    Retrieve directories containing language files for translation.

    Args:
        modules_dir (str): The directory containing all the modules.

    Returns:
        list: A list of directories containing language files for translation. Each directory represents
              a specific language and ends with the '-values' extension.

    Example:
        Input:
            get_languages_dirs('/path/to/modules')
        Output:
            ['values-ar', 'values-uk', ...]
    """
    lang_parent_dir = os.path.join(modules_dir, 'I18N', 'src', 'main', 'res')
    languages_dirs = [
        directory for directory in os.listdir(lang_parent_dir)
        if (
                directory.startswith('values')
                and 'strings.xml' in os.listdir(os.path.join(lang_parent_dir, directory))
        )
    ]
    return languages_dirs


def separate_translation_to_modules(modules_dir, lang_dir):
    """
    Separate translations from a translation file into modules.

    Args:
        modules_dir (str): The directory containing all the modules.
        lang_dir (str): The directory containing the translation file being split.

    Returns:
        dict: A dictionary containing translations split by module. The keys are module names,
              and the values are lists of dictionaries, each containing the 'key', 'value', and 'comment'
              for each translation entry within the module.

    """
    translations_roots = {}
    file_path = os.path.join(modules_dir, 'I18N', 'src', 'main', 'res', lang_dir, 'strings.xml')
    module_translations_tree = etree.parse(file_path)
    root = module_translations_tree.getroot()
    previous_entry = None
    for translation_entry in root.getchildren():
        if not isinstance(translation_entry, etree._Comment):
            module_name, key_remainder = translation_entry.attrib['name'].split('.', maxsplit=1)
            translation_entry.attrib['name'] = key_remainder

            # translations_roots.setdefault(module_name, etree.Element('resources'))
            if module_name not in translations_roots:
                translations_roots[module_name] = etree.Element('resources')

            append_element_and_comment(translation_entry, previous_entry, translations_roots[module_name])

        previous_entry = translation_entry
    return translations_roots


def split_translation_files(modules_dir=None):
    """
    Split translation files into separate files for each module and language.

    Args:
        modules_dir (str, optional): The directory containing all the modules. If not provided,
            it defaults to the parent directory of the directory containing this script.

    Returns:
        None

    Example:
        split_translation_files('/path/to/modules')
    """
    if not modules_dir:
        modules_dir = os.path.dirname(os.path.dirname(__file__))
    languages_dirs = get_languages_dirs(modules_dir)
    for lang_dir in languages_dirs:
        translations = separate_translation_to_modules(modules_dir, lang_dir)
        for module, root in translations.items():
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

