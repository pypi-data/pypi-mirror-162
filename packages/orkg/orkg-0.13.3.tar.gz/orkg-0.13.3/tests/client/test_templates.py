from unittest import TestCase
from orkg import ORKG


class TestTemplates(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """
    orkg = ORKG()

    def test_materialize(self):
        self.orkg.templates.materialize_templates()
        self.assertTrue(True)

