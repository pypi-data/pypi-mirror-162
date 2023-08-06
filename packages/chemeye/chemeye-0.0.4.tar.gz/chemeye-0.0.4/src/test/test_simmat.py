import unittest
import naclo
from chemeye import SimMat
from plotly.graph_objects import Figure


class TestSimMat(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_ecfp = naclo.mols_2_ecfp(
            naclo.smiles_2_mols([
                'CCC',
                'O',
                'C',
                'SOO'
            ]))
        return super().setUpClass()
    
    def test_init(self):
        sim_mat = SimMat(self.test_ecfp, self.test_ecfp)
        self.assertIsInstance(
            sim_mat.fig,
            Figure
        )
