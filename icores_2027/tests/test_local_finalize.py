"""Fail-closed delivery and Boolean parsing; no fabricated experiment outcomes."""
from pathlib import Path
import sys
import pandas as pd
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from local_finalize import boolean, check_experiments


def test_false_is_not_truthy_string():
    assert boolean(pd.Series(['False','True',False,True])).tolist()==[False,True,False,True]


@pytest.mark.parametrize('value',['',None,'success',1])
def test_missing_or_unrecognized_gate_is_rejected(value):
    with pytest.raises(ValueError): boolean(pd.Series([value]))


def test_missing_runs_cannot_pass_ready(tmp_path):
    with pytest.raises(FileNotFoundError): check_experiments(tmp_path/'a',tmp_path/'b')
