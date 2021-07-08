import os, sys
import pytest
from docassemble.l4.intgen import generate_interview


def test_generate_interview_rps(pytestconfig):
    get_path = lambda x : os.path.join(pytestconfig.rootpath, 'tests','test_files',x)
    with open(get_path('rps.pl'), encoding='utf-8') as scasp:
        with open(get_path('rps.yml'), encoding='utf-8') as yml:
            with open(get_path('rps.da.yml'), encoding='utf-8') as interview_yml:
                output = generate_interview(yml.read(), scasp.read())
                assert interview_yml.read() == output


def test_generate_interview_r34(pytestconfig):
    get_path = lambda x : os.path.join(pytestconfig.rootpath, 'tests','test_files',x)
    with open(get_path('r34.pl'), encoding='utf-8') as scasp:
        with open(get_path('r34.yml'), encoding='utf-8') as yml:
            with open(get_path('r34.da.yml'), encoding='utf-8') as interview_yml:
                output = generate_interview(yml.read(), scasp.read())
                assert interview_yml.read() == output
