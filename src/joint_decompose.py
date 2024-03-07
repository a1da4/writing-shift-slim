import argparse
import logging

import numpy as np
from scipy.sparse.linalg import svds
from scipy.sparse import coo_matrix
from typing import Dict, List

from sppmisvd.util import load_pickle, load_matrix


def joint(C_0: List[List[int]], C_1: List[List[int]]) -> List[List[float]]:
    return np.vstack([C_0, C_1], dtype=float)


def decompose(C: List[List[float]], dim: int) -> List[List[float]]:
    """ decompose concatenated matrix C
    :param C: List[List[float]]
    :param dim: int

    :return: decomposed matrix [len(C), dim]
    """
    U, S, _ = svds(C, k=dim)
    WV = np.dot(U, np.sqrt(np.diag(S)))

    return WV


def joint_decompose(id2word: Dict[int, str], 
                    mat_pathes: List[str], 
                    dim: int):
    """ conduct jointly decomposed (V*V or L*V -> V*D or L*D, V >> L >> D)
    :param id2word: Dict[int, str], id -> word, V words
    :param mat_pathes: List[str], path of matrices [V, V] dim
    :param dim: int, dimension (V >> dim)
    """
    logging.debug(f"[joint_decompose] load initial (C_0) mat ...")
    C_0 = load_matrix(mat_pathes[0], len(id2word))
    logging.debug(f"[joint_decompose] done")

    for i, mat_path in enumerate(mat_pathes[1:]):
        logging.debug(f"[joint_decompose] load {i+1}-th (C_{i+1}) mat ...")
        C_1 = load_matrix(mat_path, len(id2word))
        logging.debug(f"[joint_decompose] done")
        C_0 = joint(C_0, C_1)
        logging.debug(f"[joint_decompose] current: [{len(C_0)}, {len(C_0[0])}]")

    WV = decompose(C_0, dim)
    np.save(f"WV_d-{str(dim)}", WV)


def cli_main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("--pickle_id2word", help="path of id2word dict")
    parser.add_argument("--mat_pathes", nargs="*", help="pathes of cooccur/link/pmi matrices")
    parser.add_argument("--dim", type=int, default=100, help="int, dimension")
    args = parser.parse_args()

    id2word, _ = load_pickle(args.pickle_id2word)

    joint_decompose(id2word, args.mat_pathes, args.dim)


if __name__ == "__main__":
    cli_main()
