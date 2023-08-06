import pytest
import runpy
import octo

def test_version(capsys):
    runpy.run_path("octo")
    out,err = capsys.readouterr()
    print(out)

def test_help():
    assert True
