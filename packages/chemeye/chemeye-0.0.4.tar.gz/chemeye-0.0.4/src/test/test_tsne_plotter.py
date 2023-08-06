import unittest
import plotly.graph_objects as go

import naclo
from chemeye import TSNEPlotter


class TestTSNEPlotter(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_smiles = ['CN=C=O', 'CCC', 'O']
        cls.test_mols = naclo.smiles_2_mols(cls.test_smiles)
        cls.maccs_keys = naclo.mols_2_maccs(cls.test_mols)
        cls.ecfp4_prints = naclo.mols_2_ecfp(cls.test_mols, radius=2, return_numpy=True)
        
        cls.tsne_plotter = TSNEPlotter(cls.ecfp4_prints)
        return super().setUpClass()
    
    def test_plot(self):
        fig = self.tsne_plotter.plot('tsne1', 'tsne2', [1, 'a', True])
        
        self.assertIsInstance(
            fig,
            go.Figure
        )
