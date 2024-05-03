import os
from collections import OrderedDict
from lxml import etree


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
        if os.path.isdir(os.path.join(modules_dir, directory))
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

            # If there was a comment before the current element add it first.
            if isinstance(previous_element, etree._Comment):
                previous_element.tail = '\n\t'
                combined_root.append(previous_element)

            # Indent all elements with on tab.
            element.tail = '\n\t'
            combined_root.append(element)

        # To check for comments in the next round.
        previous_element = element

    return combined_root



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


def write_translation_file(modules_dir, root):
    """
    Write the contents of an ordered dictionary to a Localizable.strings file.

    This function takes an ordered dictionary containing translation data and writes it to a Localizable.strings
    file located in the 'I18N/en.lproj' directory within the specified modules directory. It creates the directory
    if it doesn't exist.

    Parameters:
       content_ordered_dict (OrderedDict): An ordered dictionary containing translation data. The keys
       are the translation keys, and the values are dictionaries with 'value' and 'comment' keys representing the
       translation value and optional comments, respectively.
       modules_dir (str): The path to the modules directory
       where the I18N directory will be written.
    """
    combined_translation_dir = os.path.join(modules_dir, 'I18N', 'values')
    os.makedirs(combined_translation_dir, exist_ok=True)

    tree = etree.ElementTree(root)
    tree.write(os.path.join(combined_translation_dir, 'strings.xml'), encoding='utf-8', xml_declaration=True)


def combine_translation_files(modules_dir=None):
    """
    Combine translation files from different modules into a single file.
    """
    if not modules_dir:
        modules_dir = os.path.dirname(os.path.dirname(__file__))
    combined_translation_dict = combine_translations(modules_dir)
    write_translation_file(modules_dir, combined_translation_dict)


if __name__ == "__main__":
    combine_translation_files()
