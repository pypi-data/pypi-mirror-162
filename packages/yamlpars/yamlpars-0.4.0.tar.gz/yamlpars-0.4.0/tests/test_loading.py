"""Test correct loading of the yaml file into the Parameters class."""
import subprocess
import unittest
from typing import Optional

from addict import Addict

from yamlpars import Parameters


class TestLoadingParameters(unittest.TestCase):
    """TestLoadingParameters class."""

    parameters: Optional[Parameters] = None
    files_involved = [
        "tests/test_yaml_folder/group_a.yaml",
        "tests/test_yaml_folder/group_b.yml",
    ]

    def setUp(self):
        self.parameters: Parameters = Parameters(
            yaml_folder="tests/test_yaml_folder", auto_load=False
        )
        self.assertFalse(self.parameters._successful_load)
        self.parameters.load()
        self.assertTrue(self.parameters._successful_load)
        self.assertIsNotNone(self.parameters)

    def tearDown(self):
        self.parameters = None
        self.assertIsNone(self.parameters)
        for file in self.files_involved:
            subprocess.run(f"git checkout HEAD -- {file}", shell=True, check=True)

    def test_00_load(self):
        self.assertIsNotNone(self.parameters.group_a)
        self.assertIsNotNone(self.parameters.group_b)
        self.assertRaises(AttributeError, lambda: self.parameters.group_c)

    def test_01_scalar(self):
        self.assertEqual(self.parameters.group_a.a_int, 1)
        self.assertIsInstance(self.parameters.group_a.a_int, int)
        self.assertEqual(self.parameters.group_a.a_float, 1.0)
        self.assertIsInstance(self.parameters.group_a.a_float, float)
        self.assertEqual(self.parameters.group_a.a_bool, True)
        self.assertIsInstance(self.parameters.group_a.a_bool, bool)

        self.assertEqual(self.parameters.group_b.b_int, -1)
        self.assertIsInstance(self.parameters.group_b.b_int, int)
        self.assertEqual(self.parameters.group_b.b_float, -1.0)
        self.assertIsInstance(self.parameters.group_b.b_float, float)
        self.assertEqual(self.parameters.group_b.b_bool, False)
        self.assertIsInstance(self.parameters.group_b.b_bool, bool)

    def test_02_dict(self):
        self.assertIsInstance(self.parameters.group_a.a_dictionary, dict)
        self.assertIsInstance(self.parameters.group_a.a_dictionary, Addict)
        self.assertEqual(self.parameters.group_a.a_dictionary.first_key, "first")
        self.assertEqual(self.parameters.group_a.a_dictionary.second_key, "second")
        self.assertEqual(self.parameters.group_a.a_dictionary.third_key, "third")
        self.assertEqual(
            self.parameters.group_a.a_deep_dict.with_several.layers, "works!"
        )

        self.assertIsInstance(self.parameters.group_b.b_dictionary, dict)
        self.assertIsInstance(self.parameters.group_b.b_dictionary, Addict)
        self.assertNotEqual(self.parameters.group_b.b_dictionary.first_key, "first")
        self.assertEqual(self.parameters.group_b.b_dictionary.first_key, "second")
        self.assertNotEqual(self.parameters.group_b.b_dictionary.second_key, "second")
        self.assertEqual(self.parameters.group_b.b_dictionary.second_key, "third")
        self.assertNotEqual(self.parameters.group_b.b_dictionary.third_key, "third")
        self.assertEqual(self.parameters.group_b.b_dictionary.third_key, "first")
        self.assertEqual(self.parameters.group_b.b_deep_dict.with_several.layers, {})

    def test_03_list(self):
        self.assertIsInstance(self.parameters.group_a.a_list, list)
        self.assertEqual(self.parameters.group_a.a_list, [0, 1, 2, 3])
        self.assertIsInstance(self.parameters.group_b.b_list, list)
        self.assertEqual(self.parameters.group_b.b_list, [0.0, 1.0, 2.0, 3.0])


if __name__ == "__main__":
    unittest.main()
