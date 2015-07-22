from unittest import TestCase

import colander

from glottolog3.models import Doctype


class Tests(TestCase):
    def test_normalize_language_explanation(self):
        from glottolog3.util import normalize_language_explanation

        for s in [' X [aaa]', 'L [aaa] = "X"', 'X = L [aaa]']:
            self.assertEquals(normalize_language_explanation(s), 'X [aaa]')

        self.assertEquals(normalize_language_explanation(' abcdefg'), 'abcdefg')

    def test_ModelInstance(self):
        from glottolog3.util import ModelInstance

        mi = ModelInstance(Doctype)
        self.assertEquals(mi.serialize(None, colander.null), colander.null)
        self.assertRaises(colander.Invalid, mi.serialize, None, '')
        self.assertEquals(mi.serialize(None, Doctype(id='id')), 'id')

        self.assertEquals(mi.deserialize(None, colander.null), colander.null)

        class Model(object):
            @classmethod
            def get(cls, val, key='id', default=None):
                if val == 'other' and key == 'alias':
                    return Model()
                if val == 'existing':
                    return Model()
                return None

        mi = ModelInstance(Model, alias='alias')
        self.assertIsInstance(mi.deserialize(None, 'other'), Model)
        self.assertIsInstance(mi.deserialize(None, 'existing'), Model)
        self.assertRaises(colander.Invalid, mi.deserialize, None, 'missing')
