import pytest
import colander

from glottolog3.models import Doctype
from glottolog3.util import normalize_language_explanation, ModelInstance


def test_normalize_language_explanation():
    #for s in [' X [aaa]', 'L [aaa] = "X"', 'X = L [aaa]']:
    #    assert normalize_language_explanation(s) == 'X [aaa]'
    assert normalize_language_explanation(' abcdefg') == 'abcdefg'


def test_ModelInstance():
    mi = ModelInstance(Doctype)
    assert mi.serialize(None, colander.null) == colander.null
    with pytest.raises(colander.Invalid):
        mi.serialize(None, '')
    assert mi.serialize(None, Doctype(id='id')) == 'id'

    assert mi.deserialize(None, colander.null) == colander.null

    class Model(object):
        @classmethod
        def get(cls, val, key='id', default=None):
            if val == 'other' and key == 'alias':
                return Model()
            if val == 'existing':
                return Model()
            return None

    mi = ModelInstance(Model, alias='alias')
    assert isinstance(mi.deserialize(None, 'other'), Model)
    assert isinstance(mi.deserialize(None, 'existing'), Model)
    with pytest.raises(colander.Invalid):
        mi.deserialize(None, 'missing')
