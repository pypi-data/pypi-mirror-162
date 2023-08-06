import unittest
import numpy as np
import naclo

from chemeye import arrays


class TestArrays(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_smiles = ['CN=C=O', 'CCC', 'O']
        cls.test_mols = naclo.smiles_2_mols(cls.test_smiles)
        cls.maccs_keys = naclo.mols_2_maccs(cls.test_mols)
        cls.ecfp4_prints = naclo.mols_2_ecfp(cls.test_mols, radius=2, return_numpy=False)
        cls.ecfp6_prints = naclo.mols_2_ecfp(cls.test_mols, radius=3, return_numpy=False)
        cls.ecfp4_prints_np = naclo.mols_2_ecfp(cls.test_mols, radius=2, return_numpy=True)
        return super().setUpClass()
    
    def test_sim_matrix(self):
        mat_maccs = arrays.sim_matrix(self.maccs_keys, self.maccs_keys, key_type='maccs')  # Test MACCS keys
        mat_ecfp4 = arrays.sim_matrix(self.ecfp4_prints, self.ecfp4_prints)  # Test ECFP4
        mat_ecfp6 = arrays.sim_matrix(self.ecfp6_prints, self.ecfp6_prints)  # Test ECFP6
        
        # Check same molecules equal 1 in matrix in all cases (along identity)
        np.testing.assert_array_equal(
            mat_maccs[np.eye(3, dtype=bool)],
            mat_ecfp4[np.eye(3, dtype=bool)],
            mat_ecfp6[np.eye(3, dtype=bool)],
            3*[1]
        )
        
        # Check maccs is different than ecfp but ecfp4,6 are equal
        self.assertFalse(
            np.array_equal(
                mat_maccs,
                mat_ecfp4
            )
        )
        self.assertTrue(
            np.array_equal(
                mat_ecfp4,
                mat_ecfp6
            )
        )
        
    def test_tsne(self):
       out = arrays.tsne(np.array(self.ecfp4_prints_np))
       self.assertEqual(
           out.shape,
           (len(self.ecfp4_prints_np), 2)
       )


if __name__ == '__main__':
    unittest.main()
