__author__ = 'xb'


def assert_dict_equals_attributes(test, d, obj):
    for k, v in d.items():
        test.assertEqual(v, getattr(obj, k))
