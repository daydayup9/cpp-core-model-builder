import xml.etree.ElementTree
from skrutil import io_utils
from skrutil import string_utils

from jni_variable import JniVariable
from jni_manager import JniManager
from skr_cpp_builder.cpp_manager import CppManagerSaveCommand
from skr_cpp_builder.cpp_manager import CppManagerFetchCommand
from skr_cpp_builder.cpp_manager import CppManagerDeleteCommand

from jni_class import JniClass


class JniModelXmlParse:

    def __init__(self, version):
        self.version = version

    def parse(self, directory):
        # create core folder if not exists and remove last build
        jni_dir_path = 'jni'
        io_utils.make_directory_if_not_exists(jni_dir_path)

        # start parsing xml
        e = xml.etree.ElementTree.parse(directory)
        root = e.getroot()

        # search directories
        for folder_node in root.findall('group'):
            group_name = folder_node.get('name')

            # search classes
            for class_node in folder_node.findall('class'):
                class_name = class_node.get('name')

                print 'Find class {0} under "{1}" group'.format(class_name, group_name)

                # parse all <variable/>
                jni_var_list = []
                for variable in class_node.findall('variable'):
                    variable_name = variable.get('name')
                    variable_type = variable.get('type')
                    variable_enum_or_none = variable.get('enum')

                    jni_var = JniVariable(variable_name, variable_type, group_name, class_name)
                    jni_var.set_enum_class_name(variable_enum_or_none)
                    jni_var_list.append(jni_var)

                # parse <manager/>
                jni_manager = None
                manager_or_none = class_node.find('manager')
                if manager_or_none is not None:
                    manager_name = manager_or_none.get('name')
                    jni_manager = JniManager(manager_name)

                    # parse all <save/>
                    for save_node in manager_or_none.findall('save'):
                        is_plural = False
                        plural_node = save_node.get('plural')
                        if plural_node is not None:
                            is_plural = True
                        save_command = CppManagerSaveCommand(is_plural)
                        jni_manager.add_save_command(save_command)

                    # parse all <delete/>
                    for delete_node in manager_or_none.findall('delete'):
                        is_plural = False
                        plural_node = delete_node.get('plural')
                        if plural_node is not None:
                            is_plural = True

                        by = delete_node.get('by')
                        delete_command = CppManagerDeleteCommand(is_plural, by)
                        jni_manager.add_delete_command(delete_command)

                    # parse all <fetch/>
                    for fetch_node in manager_or_none.findall('fetch'):
                        is_plural = False
                        plural_node = fetch_node.get('plural')
                        if plural_node is not None:
                            is_plural = True

                        by = fetch_node.get('by')
                        fetch_command = CppManagerFetchCommand(is_plural, by)
                        jni_manager.add_fetch_command(fetch_command)

                # write jni wrapper header
                jni_wrapper = JniClass(group_name, class_name, jni_var_list, jni_manager)
                jni_wrapper.generate_header()

                # write jni wrapper implementation
                jni_wrapper.generate_implementation()

                # write jni wrapper manager header
                jni_wrapper.generate_manager_header()

                # write jni wrapper manager implementation
                jni_wrapper.generate_manager_implementation()
