from docassemble.l4.intgen import *


def test_append_parent_value_empty():
    qualified_name = "legal_practice"
    apx = parent_value_apx("", "", ".value", qualified_name)
    assert apx == f"  {qualified_name}.parent_value = ''\n"


def test_append_parent_value():
    qualified_name = "legal_practice[i].joint_law_venture"
    apx = parent_value_apx("[i]", "legal_practice", ".value", qualified_name)
    assert apx == f"  {qualified_name}.parent_value = legal_practice[i].value\n"


def test_append_parent_index_value_empty():
    qualified_name = "organization"
    apx = append_parent_pfx("", "[i]", "", ".value", qualified_name)
    assert apx == f"  {qualified_name}[i].parent_value = ''\n"


def test_append_parent_index_value():
    qualified_name = "organization[i].carries_on"
    apx = append_parent_pfx("[i]", "[j]", "organization", ".value", qualified_name)
    assert apx == f"  {qualified_name}[j].parent_value = organization[i].value\n"


def test_append_any_no_any():
    input_object = {'another': 'Is there another legal practitioner in {Y}?'}
    qualified_name = "legal_practice"
    apx = append_any_apx(input_object, qualified_name)
    assert apx == f"  {qualified_name}.any = \"\"\n"


def test_append_any_with_any_no_y():
    input_object = {'any': 'Are there any legal practices?',
                    'another': 'Is there another legal practitioner in {Y}?'}
    qualified_name = "legal_practice"
    apx = append_any_apx(input_object, qualified_name)
    assert apx == f'  {qualified_name}.any = "Are there any legal practices?"\n'


def test_append_any_with_any_and_y():
    input_object = {'any': 'prefix{Y}postfix',
                    'another': 'Is there another legal practitioner in {Y}?'}
    qualified_name = "legal_practice"
    apx = append_any_apx(input_object, qualified_name)
    assert apx == f'  {qualified_name}.any = "prefix" + {qualified_name}.parent_value + "postfix"\n'


def test_append_another_no_another():
    input_object = {'any': 'Are there any legal practices?'}
    qualified_name = "legal_practice"
    apx = append_another_apx(input_object, qualified_name)
    assert apx == f"  {qualified_name}.another = \"\"\n"


def test_append_another_with_another_no_y():
    input_object = {'any': 'Are there any positions in {Y}?',
                    'another': 'Is there another legal practice?'}
    qualified_name = "legal_practice"
    apx = append_another_apx(input_object, qualified_name)
    assert apx == f'  {qualified_name}.another = "Is there another legal practice?"\n'


def test_append_another_with_another_and_y():
    input_object = {'another': 'prefix{Y}postfix'}
    qualified_name = "legal_practice"
    apx = append_another_apx(input_object, qualified_name)
    assert apx == f'  {qualified_name}.another = "prefix" + {qualified_name}.parent_value + "postfix"\n'


def test_append_ask_no_ask():
    input_object = {'any': 'Are there any positions in {Y}?'}
    qualified_name = "all_conditions_of_second_schedule_satisfied"
    apx = append_ask_apx(input_object, "", "", qualified_name)
    assert apx == f"  {qualified_name}.ask = \"\"\n"


def test_append_ask_with_ask_no_y():
    input_object = {'any': 'Are there any positions in {Y}?',
                    'ask': 'Are all the conditions of the second schedule satisfied?'}
    qualified_name = "all_conditions_of_second_schedule_satisfied"
    apx = append_ask_apx(input_object, "", "", qualified_name)
    assert apx == f'  {qualified_name}.ask = "Are all the conditions of the second schedule satisfied?"\n'


def test_append_ask_with_ask_and_y():
    input_object = {'ask': 'prefix{Y}postfix'}
    qualified_name = "service[i].law_related"
    parent = "service"
    apx = append_ask_apx(input_object, "[i]", parent, qualified_name)
    assert apx == f'  {qualified_name}.ask = "prefix" + {parent}[i].tell + "postfix"\n'


def test_append_ask_index_no_ask():
    input_object = {'any': 'Are there any positions in {Y}?'}
    qualified_name = "game[i].winner"
    apx = append_ask_index_pfx(input_object, "[i]", "[j]", "game", qualified_name)
    assert apx == f"  {qualified_name}[j].ask = \"\"\n"


def test_append_ask_index_with_ask_no_y():
    ask_str = 'What is the name of the legal practice?'
    input_object = {'any': 'Are there any positions in {Y}?',
                    'ask': ask_str}
    qualified_name = "legal_practice"
    apx = append_ask_index_pfx(input_object, "[i]", "[j]", "game", qualified_name)
    assert apx == f'  {qualified_name}[j].ask = "{ask_str}"\n'


def test_append_ask_index_with_ask_and_y():
    input_object = {'ask': 'Who is a director in {Y}?'}
    qualified_name = "organization[i].director"
    parent = "organization"
    apx = append_ask_index_pfx(input_object, "[i]", "[j]", parent, qualified_name)
    assert apx == f'  {qualified_name}[j].ask = "Who is a director in " + organization[i].tell + "?"\n'


def test_append_tell_no_tell():
    input_object = {'any': 'Are there any positions in {Y}?'}
    qualified_name = "legal_practice"
    apx = append_tell_apx(input_object, "", "", ".value", qualified_name)
    assert apx == f"---\ncode: |\n  {qualified_name}.tell = {qualified_name}.value\n"


def test_append_tell_with_tell_and_y():
    input_object = {'tell': 'prefix{X}infix{Y}postfix',
                    'type': 'str'}
    qualified_name = "service[i].law_related"
    parent = "service"
    apx = append_tell_apx(input_object, "[i]", parent, "", qualified_name)
    expected = f'''---
code: |
  {qualified_name}.tell = "prefix" + {qualified_name}.value + "infix" + {parent}[i].tell + "postfix"
'''
    assert apx == expected


def test_append_tell_idx_no_tell():
    input_object = {'any': 'Are there any positions in {Y}?',
                    'type': 'str'}
    qualified_name = "legal_practice[i].position[j].associated_with"
    apx = append_tell_idx_apx(input_object, "[i]", "[k]", "legal_practice[i].position", qualified_name)
    assert apx == f"---\ncode: |\n  {qualified_name}[k].tell = {qualified_name}[k].value\n"


def test_append_tell_idx_with_tell_and_y():
    input_object = {'tell': 'prefix{X}infix{Y}postfix',
                    'type': 'str'}
    qualified_name = "legal_practice[i].position"
    parent = "legal_practice"
    apx = append_tell_idx_apx(input_object, "[i]", "[j]", parent, qualified_name)
    expected = f'''---
code: |
  {qualified_name}[j].tell = "prefix" + {qualified_name}[j].value + "infix" + {parent}[i].tell + "postfix"
'''
    assert apx == expected


def indent_stub(indent_level):
    return lambda: " " * indent_level

def test_append_list_header_empty():
    input_object = {'name': 'legal_practice'}
    apx = append_list_header_apx(input_object, " " * 2, "")
    expected = '''  if defined('legal_practice'):
    for legal_practice_element in legal_practice:\n'''
    assert apx == expected


def test_append_list_header_value():
    input_object = {'name': 'legal_practitioner'}
    apx = append_list_header_apx(input_object, " " * 4, "legal_practice_element")
    expected = '''    if defined('legal_practice_element.legal_practitioner'):
      for legal_practitioner_element in legal_practice_element.legal_practitioner:\n'''
    assert apx == expected


def test_append_bool_elem_empty():
    input_object = {'name': 'legal_practice'}
    apx = append_bool_element_apx(input_object, indent_stub(2)(), "")
    expected = '''  if defined('legal_practice_element.value') and legal_practice_element.value:\n'''
    assert apx == expected


def test_append_bool_elem_value():
    input_object = {'name': 'legal_practitioner'}
    apx = append_bool_element_apx(input_object, indent_stub(4)(), "legal_practice")
    expected = "    if defined('legal_practice.legal_practitioner_element.value') " \
               "and legal_practice.legal_practitioner_element.value:\n"
    assert apx == expected


def test_append_var_elem_empty():
    input_object = {'name': 'legal_practice'}
    apx = append_var_element_apx(input_object, indent_stub(2)(), "")
    expected = '''  if defined('legal_practice_element.value'):\n'''
    assert apx == expected


def test_append_var_elem_value():
    input_object = {'name': 'legal_practitioner'}
    apx = append_var_element_apx(input_object, indent_stub(4)(), "legal_practice")
    expected = "    if defined('legal_practice.legal_practitioner_element.value'):\n"
    assert apx == expected


def test_append_facts_elem_empty():
    input_object = {'name': 'legal_practice'}
    apx = append_element_facts_apx(input_object, "law_practice(X)", indent_stub(2)(), "")
    expected = '''  facts += "law_practice(daSCASP_" + urllib.parse.quote_plus(str(legal_practice_element.value)).replace('%','__perc__').replace('+','__plus__') + ").\\n"\n'''
    assert apx == expected


def test_append_facts_elem_value():
    input_object = {'name': 'provides'}
    apx = append_element_facts_apx(input_object, "provides(Y,X)", indent_stub(4)(), "organization_element")
    expected = '''    facts += "provides(daSCASP_" + urllib.parse.quote_plus(str(organization_element.value)).replace('%','__perc__').replace('+','__plus__') + ",daSCASP_" + urllib.parse.quote_plus(str(provides_element.value)).replace('%','__perc__').replace('+','__plus__') + ").\\n"\n'''
    assert apx == expected


def test_append_var_bool_elem_empty():
    input_object = {'name': 'legal_practice'}
    apx = append_bool_var_apx(input_object, indent_stub(2)(), "")
    expected = '''  if defined('legal_practice.value') and legal_practice.value:\n'''
    assert apx == expected


def test_append_var_bool_elem_value():
    input_object = {'name': 'trade'}
    apx = append_bool_var_apx(input_object, indent_stub(4)(), "business_element")
    expected = "    if defined('business_element.trade.value') " \
               "and business_element.trade.value:\n"
    assert apx == expected


def test_append_var_elem_empty():
    input_object = {'name': 'legal_practice'}
    apx = append_var_apx(input_object, indent_stub(2)(), "")
    expected = '''  if defined('legal_practice.value'):\n'''
    assert apx == expected


def test_append_var_elem_value():
    input_object = {'name': 'legal_practitioner'}
    apx = append_var_apx(input_object, indent_stub(4)(), "legal_practice")
    expected = "    if defined('legal_practice.legal_practitioner.value'):\n"
    assert apx == expected


def test_append_facts_empty():
    input_object = {'name': 'legal_practice'}
    apx = append_facts_apx(input_object, "law_practice(X)", indent_stub(2)(), "")
    expected = '''  facts += "law_practice(daSCASP_" + urllib.parse.quote_plus(str(legal_practice.value)).replace('%','__perc__').replace('+','__plus__') + ").\\n"\n'''
    assert apx == expected


def test_append_facts_value():
    input_object = {'name': 'provides'}
    apx = append_facts_apx(input_object, "provides(Y,X)", indent_stub(4)(), "organization_element")
    expected = '''    facts += "provides(daSCASP_" + urllib.parse.quote_plus(str(organization_element.value)).replace('%','__perc__').replace('+','__plus__') + ",daSCASP_" + urllib.parse.quote_plus(str(organization_element.provides.value)).replace('%','__perc__').replace('+','__plus__') + ").\\n"\n'''
    assert apx == expected