"""Replay-parser regression fixtures; not substitutes for real solver checks."""
import json
from pathlib import Path
import sys

import numpy as np
import pytest

pytest.importorskip('honeybee_radiance')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from local_hb_replay import GRID, matrices, model_grid, suns


def test_effective_solar_column_order_and_diameter(tmp_path):
    p=tmp_path/'sunpath.mtx'
    p.write_text('solar510255 source sun510255\n0\n0\n4 0.2 -0.3 0.9 0.533\n'
                 'solar510285 source sun510285\n0\n0\n4 0.4 -0.5 0.8 0.533\n')
    values=suns(p)
    assert [v[0] for v in values]==['sun510255','sun510285']
    np.testing.assert_array_equal(values[1][1],[.4,-.5,.8])
    assert values[0][2]==.533


def test_tuple_json_normalization_does_not_round():
    original={'boundary':[[1.23456789012345,2.,3.]]}
    recreated={'boundary':[(1.23456789012345,2.,3.)]}
    assert original!=recreated
    assert json.loads(json.dumps(recreated))==original


def test_grid_order_preserved():
    data={'properties':{'radiance':{'sensor_grids':[{'identifier':GRID,'sensors':[
        {'pos':[3,2,.1]},{'pos':[1,4,.1]}]}]}}}
    np.testing.assert_array_equal(model_grid(data),[[3,2,.1],[1,4,.1]])


@pytest.mark.parametrize('failure',['none','shape','integration','nonbinary'])
def test_visibility_and_cumulative_contract(tmp_path,failure):
    result=tmp_path/'direct_sun_hours/results'
    (result/'direct_sun_hours').mkdir(parents=True)
    (result/'cumulative').mkdir()
    visibility=np.ones((2031,16))
    cumulative=np.full(2031,8.)
    if failure=='shape': visibility=visibility[:5]
    if failure=='integration': cumulative[0]=7.5
    if failure=='nonbinary': visibility[0,0]=.5;cumulative[0]=7.75
    np.savetxt(result/'direct_sun_hours'/f'{GRID}.ill',visibility)
    np.savetxt(result/'cumulative'/f'{GRID}.res',cumulative)
    if failure=='none':
        matrix,hours=matrices(tmp_path)
        assert matrix.shape==(2031,16) and hours.mean()==8.
    else:
        with pytest.raises(ValueError): matrices(tmp_path)
