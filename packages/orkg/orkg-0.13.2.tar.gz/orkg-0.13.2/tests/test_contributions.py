from unittest import TestCase
from orkg import ORKG


class TestContributions(TestCase):
    """
    Some test scenarios might need to be adjusted to the content of the running ORKG instance
    """
    orkg = ORKG(host='https://orkg.org/orkg', simcomp_host='https://orkg.org/orkg/simcomp')

    def test_check_simcomp(self):
        self.assertTrue(self.orkg.simcomp_available)

    def test_get_similar(self):
        res = self.orkg.contributions.similar('R3005')
        self.assertTrue(res.succeeded)

    def test_get_comparison(self):
        res = self.orkg.contributions.compare(['R3005', 'R1010'])
        self.assertTrue(res.succeeded)

    def test_get_comparison_df(self):
        res = self.orkg.contributions.compare_dataframe(contributions=['R34499', 'R34504'])
        print(res.head())

    def test_get_comparison_df_on_comparison(self):
        res = self.orkg.contributions.compare_dataframe(comparison_id='R41466')
        print(res.head())
