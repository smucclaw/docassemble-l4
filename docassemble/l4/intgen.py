# This is a script that takes a LExSIS file, and the s(CASP) with LPDAT file
# it refers to, and uses them to generate a docassemble interview that
# is designed to run on a server with docassemble-datatypes and docassemble-scasp
# installed.  This should be in the docassemble-l4 package, because it is specific
# to our implemention of scasp+lpdat.

import yaml
import docassemble.l4.relevance
from docassemble.scasp.scaspparser import term


def generate_interview(LExSIS_source, scasp_source):
    data_structure = yaml.load(LExSIS_source, Loader=yaml.FullLoader)

    # Include Docassemble-l4, which imports docassemble.scasp and docassemble.datatypes
    output = "include:\n"
    output += "  - docassemble.l4:l4.yml\n"
    output += "---\n"

    # Not sure why, but this seems to be necessary.
    output += "modules:\n"
    output += "  - docassemble.datatypes.DADataType\n"
    output += "---\n"

    # To turn on the navigation bar.
    output += "features:\n"
    output += "  navigation: True\n"
    output += "---\n"

    # Generate the parameters for DAScasp
    output += "mandatory: True \n"
    output += "code: |\n"
    output += "  ruleSource = user_info().package + \":" + data_structure['rules'] + "\"\n"
    output += "  query = \"" + data_structure['query'] + ".\"\n"
    if 'options' in data_structure:
        if 'show models' in data_structure['options']:
            output += "  show_models = " + str(data_structure['options']['show models']) + "\n"
        if 'answers' in data_structure['options']:
            if data_structure['options']['answers'] == "all":
                output += "  scasp_number = 0" + "\n"
            else:
                output += "  scasp_number = " + str(data_structure['options']['answers']) + "\n"
    output += "---\n"

    # Copy the terms from the source file
    if 'terms' in data_structure:
        output += "terms:\n"
        output += yaml.dump(data_structure['terms'], width=1000000)
        output += "---\n"

    # Include the Source File So It Can Be Accessed At RunTime
    # output += "variable name: data_structure\n"
    # output += "data:\n  "
    # output += '  '.join(yaml.dump(data_structure,width=1000000).splitlines(True))
    # output += "---\n"

    # Generate Objects Block
    output += "objects:\n"
    for var in data_structure['data']:
        output += generate_object(var)
    output += "---\n"

    # Generate Code Blocks for Lists.
    for var in data_structure['data']:
        output += make_complete_code_block(var)

    # Generate a Code Block That will Generate s(CASP) code.
    output += "code: |\n"
    output += "  import urllib\n"
    output += "  facts = \"\"\n"
    for var in data_structure['data']:
        output += generate_translation_code(var)
    output += "---\n"

    # Generate a Code Block that defines the .parent_value
    # and .self_value attribute for all objects.
    for var in data_structure['data']:
        output += generate_parent_values(var)

    # Generate Code For Agenda and Sub-Agenda
    output += generate_agendas(data_structure, scasp_source)

    # Generate Mandatory Code Block That Will Prompt Collection
    output += "mandatory: True\n"
    output += "code: |\n"
    output += "  for a in agenda:\n"
    output += "    exec(a)\n"
    output += "---\n"

    # Generate The Closing Question
    output += "mandatory: True\n"
    output += "section: Finished\n"
    output += "question: Finished\n"
    output += "subquestion: |\n"
    output += "  ${ DAScasp_show_answers }\n"
    output += "---\n"

    # Print the output (for testing)
    return output


def add_to_agenda(input_object, root=""):
    # For the main element
    # If it is a list, add it to the agenda with a .gather()
    # Otherwise, add it to the list with a .value
    # For Each Attribute
    # Add the attribute to the list.
    output = ""
    if root == "":
        dot = ""
    else:
        dot = "."
    if "[i]" not in root:
        level = "[i]"
    else:
        if "[j]" not in root:
            level = "[j]"
        else:
            if "[k]" not in root:
                level = "[k]"
            else:
                if "[l]" not in root:
                    level = "[l]"
                else:
                    if "[m]" not in root:
                        level = "[m]"
                    else:
                        raise Exception("Docassemble cannot handle nested lists of depth > 5")
    if is_list(input_object):
        new_root = root + dot + input_object['name'] + level
        this_root = root + dot + input_object['name']
    else:
        new_root = root + dot + input_object['name']
        this_root = new_root
    if is_list(input_object):
        output += "  - " + this_root + ".gather()\n"
    else:
        output += "  - " + this_root + ".value\n"
    return output


def generate_parent_values(input_object, parent="", parent_is_list=False, parent_is_objref=False):
    output = ""
    if "[i]" not in parent:
        nextlevel = "[i]"
        level = ""
    else:
        if "[j]" not in parent:
            nextlevel = "[j]"
            level = "[i]"
        else:
            if "[k]" not in parent:
                nextlevel = "[k]"
                level = "[j]"
            else:
                if "[l]" not in parent:
                    nextlevel = "[l]"
                    level = "[k]"
                else:
                    if "[m]" not in parent:
                        nextlevel = "[m]"
                        level = "[l]"
                    else:
                        raise Exception("Docassemble cannot handle nested lists of depth > 5")
    if parent == "":
        dot = ""
    else:
        dot = "."
    if parent_is_list:
        index = nextlevel
    else:
        index = level
    output += "code: |\n"
    qualified_name = parent + index + dot + input_object['name']
    output += "  " + qualified_name + '.self_value = "' + input_object['name'].replace('_', ' ') + '"\n'

    parent_value = (".value.value" if parent_is_objref else ".value")
    pv_apx = parent_value_apx(index, parent, parent_value, qualified_name)
    output += pv_apx

    if is_list(input_object):
        output += append_any_apx(input_object, qualified_name)
        output += append_another_apx(input_object, qualified_name)
    else:
        output += append_ask_apx(input_object, index, parent, qualified_name)
        output += append_tell_apx(input_object, index, parent, parent_value, qualified_name)
    output += "---\n"
    if is_list(input_object):
        if index == "[i]":
            nextindex = "[j]"
        if index == "[j]":
            nextindex = "[k]"
        if index == "[k]":
            nextindex = "[l]"
        if index == "[l]":
            nextindex = "[m]"
        if index == "":
            nextindex = "[i]"
        output += "code: |\n"
        output += "  " + qualified_name + nextindex + '.self_value = "' + input_object['name'].replace('_', ' ') + '"\n'
        output += append_parent_pfx(index, nextindex, parent, parent_value, qualified_name)
        output += append_ask_index_pfx(input_object, index, nextindex, parent, qualified_name)
        output += append_tell_idx_apx(input_object, index, nextindex, parent, qualified_name)
        output += "---\n"
    if 'attributes' in input_object:
        for a in input_object['attributes']:
            output += generate_parent_values(a, qualified_name, is_list(input_object), input_object['type'] == 'Object')
    return output


def append_tell_idx_apx(input_object, index, next_index, parent, qualified_name):
    block_pfx = "---\ncode: |\n"
    value_pfx = (".value.value" if input_object['type'] == 'Object' else ".value")
    line_prefix = "  " + qualified_name + next_index + ".tell = "
    qname_value_ref = qualified_name + next_index + value_pfx

    if 'tell' in input_object:
        x_replacement = f'" + {qname_value_ref} + "'
        x_replaced = input_object['tell'].replace('{X}', x_replacement)
        y_replacement = f'" + {parent + index}.tell + "'
        return block_pfx + line_prefix + '"' + x_replaced.replace('{Y}', y_replacement) + "\"\n"
    else:
        return block_pfx + line_prefix + qname_value_ref + "\n"


def append_tell_apx(input_object, index, parent, parent_value, qualified_name):
    block_header = "---\ncode: |\n"
    line_header = f"  {qualified_name}.tell = "
    if 'tell' in input_object:
        value_ref_pfx = ".value.value" if input_object['type'] == 'Object' else ".value"
        value_ref = f'" + {qualified_name}{value_ref_pfx} + "'
        parent_tell_ref = f'" + {parent}{index}.tell + "'
        replace_x = input_object['tell'].replace('{X}', value_ref)
        return block_header + line_header + "\"" + replace_x.replace('{Y}', parent_tell_ref) + "\"\n"
    else:
        return block_header + line_header + qualified_name + parent_value + "\n"


def append_ask_apx(input_object, index, parent, qualified_name):
    line_header = "  " + qualified_name + ".ask = \""
    line_trailer = "\"\n"

    ask_statement = input_object.get('ask', '')
    line_any_body = ask_statement.replace('{Y}', f'" + {parent}{index}.tell + "')

    return line_header + line_any_body + line_trailer


def append_ask_index_pfx(input_object, index, next_index, parent, qualified_name):
    return append_ask_apx(input_object, index, parent, qualified_name + next_index)


def append_another_apx(input_object, qualified_name):
    line_another_header = "  " + qualified_name + ".another = \""
    line_another_trailer = "\"\n"

    another_statement = input_object.get('another', '')
    line_any_body = another_statement.replace('{Y}', f'" + {qualified_name}.parent_value + "')

    return line_another_header + line_any_body + line_another_trailer


def append_any_apx(input_object, qualified_name):
    line_any_header = "  " + qualified_name + ".any = " + "\""
    line_any_trailer = "\"\n"

    any_statement = input_object.get('any', '')
    line_any_body = any_statement.replace('{Y}', f'" + {qualified_name}.parent_value + "')

    return line_any_header + line_any_body + line_any_trailer


def parent_value_apx(index, parent, line_body, qualified_name):
    line_header = "  " + qualified_name + ".parent_value = "
    line_body = parent + index + line_body if parent != "" else "''"

    return line_header + line_body + '\n'


def append_parent_pfx(index, next_index, parent, parent_value, qualified_name):
    line_header = "  " + qualified_name + next_index + ".parent_value = "
    line_body = parent + index + parent_value if parent != "" else "''"

    return line_header + line_body + '\n'


def generate_translation_code(input_object, indent_level=2, parent=""):
    # TODO: Object References should return .value.value
    output = ""

    def indent():
        return (" ") * indent_level

    # output += indent() + "# Regarding " + input_object['name'] + "\n"
    if is_list(input_object):
        output += append_list_header_apx(input_object, indent(), parent)
        indent_level += 4
        if 'encodings' in input_object:
            if input_object['type'] == "Boolean":
                output += append_bool_element_apx(input_object, indent(), parent)
            else:
                output += append_var_element_apx(input_object, indent(), parent)  # There is a problem inside
            indent_level += 2
            for e in input_object['encodings']:
                output += append_element_facts_apx(input_object, e, indent(), parent)
            # if input_object['type'] == "Boolean": # we are now indenting for everything.
            indent_level -= 2
        if 'attributes' in input_object:
            for a in input_object['attributes']:
                output += generate_translation_code(a, indent_level, input_object['name'] + "_element")
        output += indent() + "pass # to end empty for loops\n"
    else:  # This is not a list.
        if 'encodings' in input_object:
            if input_object['type'] == "Boolean":
                output += append_bool_var_apx(input_object, indent(), parent)
            else:
                output = append_var_apx(input_object, indent(), parent)
            indent_level += 2
            for e in input_object['encodings']:
                output += append_facts_apx(input_object, e, indent(), parent)
            # if input_object['type'] == "Boolean":
            indent_level -= 2
        if 'attributes' in input_object:
            for a in input_object['attributes']:
                if parent == "":
                    output += generate_translation_code(a, indent_level, input_object['name'])
                else:
                    output += generate_translation_code(a, indent_level, parent + "." + input_object['name'])
    return output


def append_facts(input_object, e, indent, parent, output):
    url_quote = "urllib.parse.quote_plus"
    replacements = "replace('%','__perc__').replace('+','__plus__')"
    if parent == "":
        x_replacement = f'''daSCASP_" + {url_quote}(str({input_object['name']}.value)).{replacements} + "'''
        facts = 'facts += "' + e.replace('X', x_replacement) + ".\\n\"\n"
        output += indent() + facts
    else:
        var_name = parent + "." + input_object['name']
        x_replacement = f'''daSCASP_" + {url_quote}(str({var_name}.value)).{replacements} + "'''
        y_replacement = f'''daSCASP_" + {url_quote}(str({parent}.value)).{replacements} + "'''
        facts = 'facts += "' + e.replace('X', x_replacement).replace('Y', y_replacement) + ".\\n\"\n"
        output += indent() + facts
    return output


def append_facts_apx(input_object, e, indent: str, parent: str):
    url_quote = "urllib.parse.quote_plus"
    replacements = "replace('%','__perc__').replace('+','__plus__')"
    if parent == "":
        x_replacement = f'''daSCASP_" + {url_quote}(str({input_object['name']}.value)).{replacements} + "'''
        facts = 'facts += "' + e.replace('X', x_replacement) + ".\\n\"\n"
    else:
        var_name = parent + "." + input_object['name']
        x_replacement = f'''daSCASP_" + {url_quote}(str({var_name}.value)).{replacements} + "'''
        y_replacement = f'''daSCASP_" + {url_quote}(str({parent}.value)).{replacements} + "'''
        facts = 'facts += "' + e.replace('X', x_replacement).replace('Y', y_replacement) + ".\\n\"\n"
    return indent + facts


def append_element_facts_apx(input_object, e: str, indent: str, parent: str) -> str:
    replacements = "replace('%','__perc__').replace('+','__plus__')"
    url_quote = "urllib.parse.quote_plus"
    x_replacement = f'''daSCASP_" + {url_quote}(str({input_object['name']}_element.value)).{replacements} + "'''
    y_replacement = f'''daSCASP_" + {url_quote}(str({parent}.value)).{replacements} + "'''

    if parent == "":
        facts = e.replace('X', x_replacement)
    else:
        facts = e.replace('X', x_replacement).replace('Y', y_replacement)

    return indent + "facts += \"" + facts + ".\\n\"\n"


def append_var_element_apx(input_object, indent: str, parent: str) -> str:
    if parent == "" or parent.endswith("_element"):
        var_name = input_object['name'] + "_element.value"
    else:
        # THIS IS THE PROBLEM
        var_name = parent + "." + input_object['name'] + "_element.value"
    return indent + "if defined('" + var_name + "'):\n"


def append_var(input_object, indent, parent, output):
    if parent == "":
        var_name = input_object['name'] + ".value"
    else:
        var_name = parent + "." + input_object['name'] + ".value"

    output += indent() + "if defined('" + var_name + "'):\n"
    return output


def append_var_apx(input_object, indent: str, parent: str) -> str:
    if parent == "":
        var_name = input_object['name'] + ".value"
    else:
        var_name = parent + "." + input_object['name'] + ".value"

    return indent + "if defined('" + var_name + "'):\n"


def append_bool_element_apx(input_object, indent: str, parent: str) -> str:
    if parent == "" or parent.endswith("_element"):
        bool_var = input_object['name'] + "_element.value"
    else:
        bool_var = parent + "." + input_object['name'] + "_element.value"
    return indent + f"if defined('{bool_var}') and {bool_var}:\n"


def append_bool_var_apx(input_object, indent: str, parent: str) -> str:
    if parent == "":
        bool_var_name = input_object['name'] + ".value"
    else:
        bool_var_name = parent + "." + input_object['name'] + ".value"

    return indent + f"if defined('{bool_var_name}') and {bool_var_name}:\n"


def append_list_header_apx(input_object, indent, parent):
    it_element_name = input_object['name'] + "_element"

    container_name = input_object['name'] if parent == "" else parent + "." + input_object['name']

    guard_line = indent + f"if defined('{container_name}'):\n"
    for_line = indent + f"  for {it_element_name} in {container_name}:\n"
    return guard_line + for_line


def make_complete_code_block(input_object, root=""):
    output = ""
    if root == "":
        dot = ""
    else:
        dot = "."
    if "[i]" not in root:
        level = "[i]"
    else:
        if "[j]" not in root:
            level = "[j]"
        else:
            if "[k]" not in root:
                level = "[k]"
            else:
                if "[l]" not in root:
                    level = "[l]"
                else:
                    if "[m]" not in root:
                        level = "[m]"
                    else:
                        raise Exception("Docassemble cannot handle nested lists of depth > 5")
    if is_list(input_object):
        new_root = root + dot + input_object['name'] + level
    else:
        new_root = root + dot + input_object['name']
    if is_list(input_object):
        output += "code: |\n"
        output += "  " + new_root + ".value\n"
        if 'attributes' in input_object:
            for a in input_object['attributes']:
                # TODO: In here, we need to check to see if the object is a reference
                # to something higher up the data structure, and if so, exclude it here
                # and add it to the agenda after the target has been collected.
                if is_list(a):
                    output += "  if \"" + new_root + "." + a['name'] + ".gather()\" in subagenda:\n"
                    output += "    " + new_root + "." + a['name'] + ".gather()\n"
                else:
                    output += "  if \"" + new_root + "." + a['name'] + ".value\" in subagenda:\n"
                    output += "    " + new_root + "." + a['name'] + ".value\n"
        output += "  " + new_root + ".complete =  True\n"
        output += "---\n"
    if 'attributes' in input_object:
        for a in input_object['attributes']:
            output += make_complete_code_block(a, new_root)
    return output


def generate_object(input_object, root=""):
    if root == "":
        dot = ""
    else:
        dot = "."
    if "[i]" not in root:
        level = "[i]"
    else:
        if "[j]" not in root:
            level = "[j]"
        else:
            if "[k]" not in root:
                level = "[k]"
            else:
                if "[l]" not in root:
                    level = "[l]"
                else:
                    if "[m]" not in root:
                        level = "[m]"
                    else:
                        raise Exception("Docassemble cannot handle nested lists of depth > 5")
    if is_list(input_object):
        new_root = root + dot + input_object['name'] + level
        this_root = root + dot + input_object['name']
    else:
        new_root = root + dot + input_object['name']
        this_root = new_root
    output = "  - " + this_root + ": |\n      "
    if is_list(input_object):
        output += "DAList.using(object_type=" + generate_DADTDataType(input_object['type'])
        if input_object['type'] == "Enum":
            output += ".using(options=" + input_object['options'] + ")"
        if input_object['type'] == "Object":
            output += ".using(source=" + input_object['source'] + ")"
        if 'minimum' in input_object:
            output += ",minimum=" + str(input_object['minimum'])
        if 'maximum' in input_object:
            output += ",maximum=" + str(input_object['maximum'])
        if 'exactly' in input_object:
            output += ",target_number=" + str(input_object['exactly'])
        if 'exactly' in input_object:
            output += ",ask_number=True"
        # The following treats optional single elements as lists of max length 1.
        if 'minimum' in input_object and 'maximum' in input_object:
            if input_object['minimum'] == 0 and input_object['maximum'] == 1:
                output += ",there_is_another=False"
        output += ",complete_attribute=\"complete\")\n"
    else:
        if input_object['type'] == "Enum":
            output += generate_DADTDataType(input_object['type']) + ".using(options="
            output += str(input_object['options']) + ")\n"
        else:
            if input_object['type'] == "Object":
                output += generate_DADTDataType(input_object['type']) + ".using(source="
                output += input_object['source'] + ")\n"
            else:
                output += generate_DADTDataType(input_object['type']) + "\n"

    if 'attributes' in input_object:
        for a in input_object['attributes']:
            output += generate_object(a, new_root)
    return output


dadatatypes = {
    "Boolean": "DADTBoolean",
    "Continue": "DADTContinue",
    "String": "DADTString",
    "Enum": "DADTEnum",
    "Number": "DADTNumber",
    "Date": "DADTDate",
    "DateTime": "DADTDateTime",
    "Time": "DADTTime",
    "YesNoMaybe": "DADTYesNoMaybe",
    "File": "DADTFile",
    "Object": "DADTObjectRef"
}


def generate_DADTDataType(input_type):
    if input_type not in dadatatypes:
        raise Exception("Unknown datatpye.")
    return dadatatypes.get(input_type)


def is_list(input):
    # Something with exactly 1 or 0 values is not a list.
    if 'exactly' in input and (input['exactly'] == 1 or input['exactly'] == 0):
        return False
    # Something with a minimum of more than one, or with a minumum and no maximum
    # is a list
    if 'minimum' in input:
        if input['minimum'] > 1:
            return True
        if 'maximum' not in input:
            return True
    # Something with a maximum above one is a list
    if 'maximum' in input and input['maximum'] > 1:
        return True
    # Something with an exact number above 1 is a list
    if 'exactly' in input and input['exactly'] > 1:
        return True
    # Something that is optional should be treated as though it was a list
    # in that you should ask whether it exists before collecting it, but only
    # collect the one.
    if 'minimum' in input and 'maximum' in input:
        if input['minimum'] == 0 and input['maximum'] == 1:
            return True
    # Otherwise
    return False


def generate_agendas(data_structure, sCASP):
    # Get the query from the LExSIS data
    query = data_structure['query']
    # Figure out what predicates are relevant leaves from the relevance module
    relevant_preds = docassemble.l4.relevance.relevant_to(sCASP, query)

    # Go through the data structure, and record the names of all data elements
    # with relevant encodings or children with relevant encodings.
    relevant_root = []
    relevant_sub = []

    for d in data_structure['data']:
        (relroot, relsub) = find_relevant(d, relevant_preds)
        relevant_root += relroot
        relevant_sub += relsub

    relevant_root.sort(key=is_target, reverse=True)

    output = "variable name: agenda\n"
    output += "data:\n"
    # Add agenda here
    # Leave only the targeted ones if there are duplicates.
    undup_relevant_root = [x for x in relevant_root if x + " #TARGET" not in relevant_root]
    # list(dict.fromkeys(list)) is just a way to remove duplicates and maintain order.
    for rr in list(dict.fromkeys(undup_relevant_root)):
        without_gather = rr.replace('.gather()', '')
        without_value = without_gather.replace('.value', '')
        cleaned_rr = without_value.replace(' #TARGET', '')
        output += "  - nav.set_section('" + cleaned_rr + "_review')\n"
        output += "  - " + rr + "\n"
    output += "---\n"
    output += "variable name: subagenda\n"
    output += "data:\n"
    # Add sub-agenda here
    for rs in list(dict.fromkeys(relevant_sub)):
        output += "  - " + rs + "\n"
    output += "---\n"

    # Add sections (done after agenda to get the same ordering)
    output += "sections:\n"
    for d in list(dict.fromkeys(undup_relevant_root)):
        without_gather = d.replace('.gather()', '')
        without_value = without_gather.replace('.value', '')
        cleaned_d = without_value.replace(' #TARGET', '')
        output += "  - " + cleaned_d + "_review: " + cleaned_d.replace('_', ' ').capitalize() + "\n"
    output += "  - finished: Finished\n"
    output += "---\n"

    return output


def find_relevant(data_element, relevant_preds, parent="", list_level=0, root=True):
    output = []
    suboutput = []
    if parent == "":
        current = data_element['name']
        dot = ""
    else:
        current = parent + "." + data_element['name']
        dot = "."
    if is_list(data_element):
        current += "[" + "ijklm"[list_level] + "]"
        trailer = ".gather()"
    else:
        trailer = ".value"
    if 'encodings' in data_element:
        for e in data_element['encodings']:
            if docassemble.l4.relevance.generalize(term.parseString(e)) in relevant_preds:
                if root:
                    output.append(parent + dot + data_element['name'] + trailer)
                else:
                    suboutput.append(parent + dot + data_element['name'] + trailer)
                # If there is an object reference in a relevant data_element, the source object is also relevant.
                if data_element['type'] == "Object":
                    output.append(data_element['source'] + ".gather() #TARGET")  # Sources are always root objects.
    if 'attributes' in data_element:
        for a in data_element['attributes']:
            (new, subnew) = find_relevant(a, relevant_preds, current, list_level + 1, False)
            if len(subnew):
                if root:
                    output.append(parent + dot + data_element['name'] + trailer)
                else:
                    suboutput.append(parent + dot + data_element['name'] + trailer)
            suboutput += subnew
            output += new

    return (output, suboutput)


def is_target(agenda_item):
    return agenda_item.endswith(" #TARGET")
