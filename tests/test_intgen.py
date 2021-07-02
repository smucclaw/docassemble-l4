from docassemble.l4.intgen import parent_value_apx, append_any_apx, append_another_apx, append_ask_apx, append_tell_apx, \
    append_parent_pfx, append_ask_index, append_ask_index_pfx


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
