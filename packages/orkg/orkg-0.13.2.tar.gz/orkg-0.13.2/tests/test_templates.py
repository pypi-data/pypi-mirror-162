from unittest import TestCase
from orkg import ORKG


class TestTemplates(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """
    orkg = ORKG(host="https://incubating.orkg.org/")

    def test_materialize(self):
        self.orkg.templates.materialize_template(template_id="R12002")
        print(self.orkg.templates.list_templates())
        self.assertTrue(True)

