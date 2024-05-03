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


def get_translations(modules_dir):
    """
    Retrieve the translations from all specified modules as OrderedDict.

    Parameters:
        modules_dir (str): The directory containing the modules.

    Returns:
        {
        module: [
                {
                    'name': 'long_name',
                    'tag_type': string, string-array, or plurals,
                    'product': product_number or None,
                    'items': [],
                    'comment': comment_tag,
                }.
                {
                    etc
                },
            ]
        }
        OrderedDict of dict: An ordered dict of dictionaries containing the 'key', 'value', and 'comment' for each
        translation line. The key of the outer OrderedDict consists of the value of the translation key combined with
        the name of the module containing the translation.
    """
    combined_root = etree.Element('resources')

    modules = get_modules_to_translate(modules_dir)
    for module in modules:
        translation_file = get_translation_file_path(modules_dir, module)
        module_translations_tree = etree.parse(translation_file)
        root = module_translations_tree.getroot()

        previous_element = None

        for element in root.getchildren():
            # if translatable, either 'string', 'string-array', or 'plurals' and there is no ignor in that tag:
            translatable = element.attrib.get('translatable', True)
            if (
                    translatable and translatable != 'false'
                    and element.tag in ['string', 'string-array', 'plurals']
                    and element.nsmap
                    and not element.attrib.get('{%s}ignore' % element.nsmap["tools"])
            ):

                new_element = element
                new_element.attrib['name'] = '.'.join([module, element.attrib.get('name')])

                if isinstance(previous_element, etree._Comment):
                    combined_root.append(previous_element)

                combined_root.append(new_element)

                # translation_entry = {
                #     'name': element.attrib.get('name'),
                #     'tag_type': element.tag,
                # }
                #
                # product_property = element.attrib.get('product')
                # if product_property:
                #     translation_entry['product'] = product_property
                #
                # if isinstance(previous_element, etree._Comment):
                #     translation_entry['comment'] = previous_element
                #
                # if element.tag in ['string-array', 'plurals']:
                #     translation_entry['items'] = []
                #     for item in element.getchildren():
                #         item_data = {'text': item.text}
                #         quantity_property = item.attrib.get('quantity')
                #         if quantity_property:
                #             item_data['quantity'] = quantity_property
                #         translation_entry['items'].append(item_data)
                #
                # elif element.tag == 'string':
                #     translation_entry['text'] = element.text
                #
                # translations_dict[module].append(translation_entry)
            previous_element = element

    return combined_root


def get_languages(modules_dir):
    languages = set()
    modules = [
        module for module in os.listdir(modules_dir)
        if os.path.exists(os.path.join(modules_dir, module, 'src', 'main', 'res'))  # ==> is_translatable_module

    ]
    for module in modules:
        if os.path.isdir(os.path.join(modules_dir, module, 'src', 'main', 'res')):
            lang_list = [elem.strip('values') for elem in os.listdir(os.path.join(modules_dir, module, 'src', 'main', 'res'))
                         if elem.startswith('values')]
            languages.update(lang_list)
    return languages


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

    # with open(os.path.join(combined_translation_dir, 'strings.xml'), 'w') as f:
    tree = etree.ElementTree(root)
    tree.write(os.path.join(combined_translation_dir, 'strings.xml'), encoding='utf-8', xml_declaration=True)

#
# def write_in_file(f, module, module_dict):
#     for element in module_dict:
#         comment = element.get('comment')  # Retrieve the comment, if present
#         if comment:
#             f.write(comment)
        # f.write(f'"{key}" = "{value["value"]}";\n')

def combine_translation_files(modules_dir=None):
    """
    Combine translation files from different modules into a single file.
    """
    if not modules_dir:
        modules_dir = os.path.dirname(os.path.dirname(__file__))
    combined_translation_dict = get_translations(modules_dir)
    write_translation_file(modules_dir, combined_translation_dict)


if __name__ == "__main__":
    combine_translation_files()
