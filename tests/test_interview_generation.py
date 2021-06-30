import os

from docassemble.l4.intgen import generate_interview

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_files',
)



def test_generate_interview():
    with open('test_files/rps.pl') as scasp:
        with open('test_files/rps.yml') as yml:
            output = generate_interview(yml.read(), scasp.read())
            print(output)
