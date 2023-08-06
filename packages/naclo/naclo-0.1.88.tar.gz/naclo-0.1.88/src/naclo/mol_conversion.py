import warnings
from rdkit import Chem
import numpy as np
from rdkit.Chem import AllChem, MACCSkeys, DataStructs
from typing import Iterable, List, Union, Optional
import pandas as pd
from stse.dataframes import z_norm as stse_z_norm


def mols_2_smiles(mols:Iterable[Chem.rdchem.Mol]) -> List[str]:  # *
    """Generates SMILES strings from list of rdkit Mol objects.

    Args:
        mols (Iterable[Chem.rdchem.Mol]): Contains RDKit Mols.

    Returns:
        List[str]: Contains SMILES strings.
    """
    return [Chem.MolToSmiles(mol) for mol in mols]

def smiles_2_mols(smiles:Iterable[str]) -> List[Chem.rdchem.Mol]:  # *
    """Generates rdkit Mol objects from SMILES strings.

    Args:
        smiles (Iterable[str]): Contains SMILES strings.

    Returns:
        List[Chem.rdchem.Mol]: Contains RDKit Mols.
    """
    return [Chem.MolFromSmiles(smile) for smile in smiles]

def mols_2_inchi_keys(mols):  # *
    """Generates InChI key strings from rdkit Mol objects.

    Args:
        mols (iter[rdkit Mols]): Contains rdkit Mols.

    Returns:
        list[str]: Contains InChI key strings.
    """
    return [Chem.MolToInchiKey(mol) for mol in mols]

def smiles_2_inchi_keys(smiles:Iterable[str]) -> List[str]:  # *
    """Generates InChI key strings from SMILES strings.

    Args:
        smiles (Iterable[str]): Contains SMILES strings.

    Returns:
        List[str]: Contains InChI key strings.
    """
    return mols_2_inchi_keys(smiles_2_mols(smiles))

def mols_2_ecfp(mols:Iterable[Chem.rdchem.Mol], radius:int=2, return_numpy:bool=False,
                n_bits:Optional[int]=1024,
                use_chirality:bool=True) -> List[Union[np.array, DataStructs.cDataStructs.UIntSparseIntVect]]:
    """Converts from rdkit mol objects to morgan fingerprints (full ECFP6).

    :param mols: Collection of mols
    :type mols: list[rdkit mol]
    :param radius: ECFP radius, defaults to 3 (ECFP6)
    :type radius: int, optional
    :return: Collection of ECFP vectors
    :rtype: list[rdkit BitVect]
    """
    if not n_bits:
        if return_numpy:
            warnings.warn('Cannot return numpy array if n_bits is None. Returning \
                DataStructs.cDataStructs.UIntSparseIntVect instead.', UserWarning)
        return [AllChem.GetMorganFingerprint(m, radius, useChirality=use_chirality) for m in mols]
    else:
        fingerprints = [AllChem.GetMorganFingerprintAsBitVect(m, radius, useChirality=use_chirality, nBits=n_bits) \
            for m in mols]
        
        if return_numpy:
            X = []
            for fp in fingerprints:
                arr = np.array([])
                DataStructs.ConvertToNumpyArray(fp, arr)
                X.append(arr)
            return X
        return fingerprints

def mols_2_maccs(mols:Iterable[Chem.rdchem.Mol]) -> List[DataStructs.cDataStructs.ExplicitBitVect]:
    """Converts from mol objects to MACCS keys.

    :param mols: Collection of molecules
    :type mols: list[rdkit mol]
    :return: Collection of MACCS keys
    :rtype: list[rdkit BitVect]
    """
    return [MACCSkeys.GenMACCSKeys(m) for m in mols]

def mols_2_ecfp_plus_descriptors(mols:Iterable[Chem.rdchem.Mol], other_df:pd.DataFrame, z_norm:bool=True,
                          ecfp_radius:int=2, ecfp_n_bits:int=1024) -> np.array:
    ecfp_X = mols_2_ecfp(mols, radius=ecfp_radius, n_bits=ecfp_n_bits, return_numpy=True)
    other_X = stse_z_norm(other_df).to_numpy() if z_norm else other_df.to_numpy()
    return np.concatenate((ecfp_X, other_X), axis=1)
