# This is a script that takes a LExSIS file, and the s(CASP) with LPDAT file
# it refers to, and uses them to generate a docassemble interview that
# is designed to run on a server with docassemble-datatypes and docassemble-scasp
# installed.  This should be in the docassemble-l4 package, because it is specific
# to our implemention of scasp+lpdat.

import yaml
import docassemble.l4.relevance
from  docassemble.scasp.scaspparser import term

def generate_interview(LExSIS_source,scasp_source):
    data_structure = yaml.load(LExSIS_source, Loader=yaml.FullLoader)
    
    ## Include Docassemble-l4, which imports docassemble.scasp and docassemble.datatypes
    output = "include:\n"
    output += "  - docassemble.l4:l4.yml\n"
    output += "---\n"

    ## Not sure why, but this seems to be necessary.
    output += "modules:\n"
    output += "  - docassemble.datatypes.DADataType\n"
    output += "---\n"

    ## Generate the parameters for DAScasp
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

    ## Copy the terms from the source file
    if 'terms' in data_structure:
        output += "auto terms:\n"
        output += yaml.dump(data_structure['terms'],width=1000000)
        output += "---\n"

    ## Include the Source File So It Can Be Accessed At RunTime
    output += "variable name: data_structure\n"
    output += "data:\n  "
    output += '  '.join(yaml.dump(data_structure,width=1000000).splitlines(True))
    output += "---\n"


    ## Generate Objects Block
    output += "objects:\n"
    for var in data_structure['data']:
        output += generate_object(var)
    output += "---\n"

    ## Generate Code Blocks for Lists.
    for var in data_structure['data']:
        output += make_complete_code_block(var)

    ## Generate a Code Block That will Generate s(CASP) code.
    output += "code: |\n"
    output += "  import urllib\n"
    output += "  facts = \"\"\n"
    for var in data_structure['data']:
        output += generate_translation_code(var)
    output += "---\n"

    ## Generate a Code Block that defines the .parent_value
    ## and .self_value attribute for all objects.
    for var in data_structure['data']:
        output += generate_parent_values(var)

    ## Generate Code For Agenda and Sub-Agenda
    output += generate_agendas(data_structure,scasp_source)

    ## Generate Mandatory Code Block That Will Prompt Collection
    output += "mandatory: True\n"
    output += "code: |\n"
    output += "  for a in agenda:\n"
    output += "    exec(a)\n"
    output += "---\n"

    ## Generate The Closing Question
    output += "mandatory: True\n"
    output += "question: Finished\n"
    output += "subquestion: |\n"
    output += "  ${ DAScasp_show_answers }\n"
    output += "---\n"

    ## Print the output (for testing)
    return output

def add_to_agenda(input_object,root=""):
    #For the main element
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

def generate_parent_values(input_object,parent="",parent_is_list=False,parent_is_objref=False):
    output = ""
    if "[i]" not in parent:
        nextlevel = "[i]"
        level=""
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
    output += "  " + parent + index + dot + input_object['name'] + '.self_value = "' + input_object['name'].replace('_',' ') + '"\n'
    if parent != "": # This object has a parent
        output += "  " + parent + index + dot + input_object['name'] + ".parent_value = " + parent + index + (".value.value" if parent_is_objref else ".value") + "\n"
    else:
        output += "  " + parent + index + dot + input_object['name'] + ".parent_value = ''\n"
    if is_list(input_object):
        if 'any' in input_object:
            output += "  " + parent + index + dot + input_object['name'] + ".any = \"" + input_object['any'].replace('{Y}',"\" + " + parent + index + dot + input_object['name'] + ".parent_value + \"") + "\"\n"
        else:
            output += "  " + parent + index + dot + input_object['name'] + ".any = \"\"\n"
        if 'another' in input_object:
            output += "  " + parent + index + dot + input_object['name'] + ".another = \"" + input_object['another'].replace('{Y}',"\" + " + parent + index + dot + input_object['name'] + ".parent_value + \"") + "\"\n"
        else:
            output += "  " + parent + index + dot + input_object['name'] + ".another = \"\"\n"
    else:
        if 'ask' in input_object:
            output += "  " + parent + index + dot + input_object['name'] + ".ask = \"" + input_object['ask'].replace('{Y}',"\" + " + parent + index + ".tell + \"") + "\"\n"
        else:
            output += "  " + parent + index + dot + input_object['name'] + ".ask = \"\"\n"
        if 'tell' in input_object:
            output += "---\ncode: |\n"
            output += "  " + parent + index + dot + input_object['name'] + ".tell = \"" + input_object['tell'].replace('{X}',"\" + " + parent + index + dot + input_object['name'] + (".value.value" if input_object['type'] == 'Object' else ".value") + " + \"").replace('{Y}',"\" + " + parent + index + ".tell + \"") + "\"\n"
        else:
            output += "---\ncode: |\n"
            output += "  " + parent + index + dot + input_object['name'] + ".tell = " + parent + index + dot + input_object['name'] + (".value.value" if parent_is_objref else ".value") + "\n"    
    output += "---\n"
    if is_list(input_object):
        if index == "[i]": nextindex = "[j]"
        if index == "[j]": nextindex = "[k]"
        if index == "[k]": nextindex = "[l]"
        if index == "[l]": nextindex = "[m]"
        if index == "": nextindex = "[i]"
        output += "code: |\n"
        output += "  " + parent + index + dot + input_object['name'] + nextindex + '.self_value = "' + input_object['name'].replace('_',' ') + '"\n'
        if parent != "": # This object has a parent
            output += "  " + parent + index + dot + input_object['name'] + nextindex + ".parent_value = " + parent + index + (".value.value" if parent_is_objref else ".value") + '\n'
        else:
            output += "  " + parent + index + dot + input_object['name'] + nextindex + ".parent_value = ''\n"
        if 'ask' in input_object:
            output += "  " + parent + index + dot + input_object['name'] + nextindex + ".ask = \"" + input_object['ask'].replace('{Y}',"\" + " + parent + index + ".tell + \"") + "\"\n"
        else:
            output += "  " + parent + index + dot + input_object['name'] + nextindex + ".ask = \"\"\n"
        if 'tell' in input_object:
            output += "---\ncode: |\n"
            output += "  " + parent + index + dot + input_object['name'] + nextindex + ".tell = \"" + input_object['tell'].replace('{X}',"\" + " + parent + index + dot + input_object['name'] + nextindex + (".value.value" if input_object['type'] == 'Object' else ".value") + " + \"").replace('{Y}',"\" + " + parent + index + ".tell + \"") + "\"\n"
        else:
            output += "---\ncode: |\n"
            output += "  " + parent + index + dot + input_object['name'] + nextindex + ".tell = " + parent + index + dot + input_object['name'] + nextindex + (".value.value" if input_object['type'] == 'Object' else ".value") + "\n"  
        output += "---\n"
    if 'attributes' in input_object:
        for a in input_object['attributes']:
            output += generate_parent_values(a,parent + index + dot + input_object['name'],is_list(input_object),input_object['type'] == 'Object')
    return output

def generate_translation_code(input_object,indent_level=2,parent=""):
    # TODO: Object References should return .value.value
    output = ""
    def indent(): return (" ") * indent_level
    # output += indent() + "# Regarding " + input_object['name'] + "\n"
    if is_list(input_object):
        if parent == "": # This is a root list
            output += indent() + "if defined('" + input_object['name'] + "'):\n"
            output += indent() + "  for " + input_object['name'] + "_element in " + input_object['name'] + ":\n"
        else: # This is a non-root list
            output += indent() + "if defined('" + parent + "." + input_object['name'] + "'):\n"
            output += indent() + "  for " + input_object['name'] + "_element in " + parent + "." + input_object['name'] + ":\n"
        indent_level += 4
        if 'encodings' in input_object:
            if input_object['type'] == "Boolean":
                if parent == "" or parent.endswith("_element"):
                    output += indent() + "if defined('" + input_object['name'] + "_element.value') and " + input_object['name'] + "_element.value:\n"
                else:
                    output += indent() + "if defined('" + parent + "." + input_object['name'] + "_element.value') and " + parent + "." + input_object['name'] + "_element.value:\n"
            else:
                if parent == "" or parent.endswith("_element"):
                    output += indent() + "if defined('" + input_object['name'] + "_element.value'):\n"
                else:
                    output += indent() + "if defined('" + parent + "." + input_object['name'] + "_element.value'):\n" # THIS IS THE PROBLEM
            indent_level += 2
            for e in input_object['encodings']:
                if parent == "":
                    output += indent() + "facts += \"" + e.replace('X',"daSCASP_\" + urllib.parse.quote_plus(str(" + input_object['name'] + "_element.value)).replace('%','__perc__').replace('+','__plus__') + \"") + ".\\n\"\n"
                else:
                    output += indent() + "facts += \"" + e.replace('X',"daSCASP_\" + urllib.parse.quote_plus(str(" + input_object['name'] + "_element.value)).replace('%','__perc__').replace('+','__plus__') + \"").replace('Y',"daSCASP_\" + urllib.parse.quote_plus(str(" + parent + ".value)).replace('%','__perc__').replace('+','__plus__') + \"") + ".\\n\"\n"
            # if input_object['type'] == "Boolean": # we are now indenting for everything.
            indent_level -= 2
        if 'attributes' in input_object:
            for a in input_object['attributes']:
                output += generate_translation_code(a,indent_level,input_object['name'] + "_element")
        output += indent() + "pass # to end empty for loops\n"
    else: # This is not a list.
        if 'encodings' in input_object:
            if input_object['type'] == "Boolean":
                if parent == "":
                    output += indent() + "if defined('" + input_object['name'] + ".value') and " + input_object['name'] + ".value:\n"
                else:
                    output += indent() + "if defined('" + parent + "." + input_object['name'] + ".value') and " + parent + "." + input_object['name'] + ".value:\n"
            else:
                if parent == "":
                    output += indent() + "if defined('" + input_object['name'] + ".value'):\n"
                else:
                    output += indent() + "if defined('" + parent + "." + input_object['name'] + ".value'):\n"
            indent_level += 2
            for e in input_object['encodings']:
                if parent == "":
                    output += indent() + "facts += \"" + e.replace('X',"daSCASP_\" + urllib.parse.quote_plus(str(" + input_object['name'] + ".value)).replace('%','__perc__').replace('+','__plus__') + \"") + ".\\n\"\n"
                else:
                    output += indent() + "facts += \"" + e.replace('X',"daSCASP_\" + urllib.parse.quote_plus(str(" + parent + "." + input_object['name'] + ".value)).replace('%','__perc__').replace('+','__plus__') + \"").replace('Y',"daSCASP_\" + urllib.parse.quote_plus(str(" + parent + ".value)).replace('%','__perc__').replace('+','__plus__') + \"") + ".\\n\"\n"
            #if input_object['type'] == "Boolean":
            indent_level -= 2
        if 'attributes' in input_object:
            for a in input_object['attributes']:
                if parent == "":
                    output += generate_translation_code(a,indent_level,input_object['name'])
                else:
                    output += generate_translation_code(a,indent_level,parent + "." + input_object['name'])
    return output

def make_complete_code_block(input_object,root=""):
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
            output += make_complete_code_block(a,new_root)
    return output

def generate_object(input_object,root=""):
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
            output += generate_object(a,new_root)
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

def generate_agendas(data_structure,sCASP):
    # Get the query from the LExSIS data
    query = data_structure['query']
    # Figure out what predicates are relevant leaves from the relevance module
    relevant_preds = docassemble.l4.relevance.relevant_to(sCASP,query)

    # Go through the data structure, and record the names of all data elements
    # with relevant encodings or children with relevant encodings.
    relevant_root = []
    relevant_sub = []
    
    
    for d in data_structure['data']:
        (relroot,relsub) = find_relevant(d,relevant_preds)
        relevant_root += relroot
        relevant_sub += relsub
    
    relevant_root.sort(key=is_target,reverse=True)

    output = "variable name: agenda\n"
    output += "data:\n"
    # Add agenda here
    for rr in list(dict.fromkeys(relevant_root)): # list(dict.fromkeys(list)) is just a way to remove duplicates and maintain order.
        output += "  - " + rr + "\n"
    output += "---\n"
    output += "variable name: subagenda\n"
    output += "data:\n"
    # Add sub-agenda here
    for rs in set(relevant_sub):
        output += "  - " + rs + "\n"
    output += "---\n"

    return output

def find_relevant(data_element,relevant_preds,parent="",list_level=0,root=True):
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
        new_list = list_level + 1
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
                if data_element['type'] == "Object": # If there is an object reference in a relevant data_element, the source object is also relevant.
                    output.append(data_element['source'] + ".gather() #TARGET") #Sources are always root objects.
    if 'attributes' in data_element:
        for a in data_element['attributes']:
            (new,subnew) = find_relevant(a,relevant_preds,current,new_list,False)
            if len(subnew):
                if root:
                    output.append(parent + dot + data_element['name'] + trailer)
                else:
                    suboutput.append(parent + dot + data_element['name'] + trailer)
            suboutput += subnew
            output += new

    return (output,suboutput)

def is_target(agenda_item):
    return agenda_item.endswith(" #TARGET")