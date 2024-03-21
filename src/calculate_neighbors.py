import argparse
import logging
import pickle

import numpy as np
from scipy.spatial.distance import cdist
from typing import Dict, List

from sppmisvd.util import load_pickle


def get_target_ids(word2id: Dict[str, int],
                   target_words: List[str]) -> Dict[int, str]:
    id2target = {}
    for target_word in target_words:
        if target_word in word2id:
            target_id = word2id[target_word]
            id2target[target_id] = target_word
        else:
            logging.info(f"[get_target_ids] {target_word} does not exist")
    return id2target


def calculate_neighbors(id2word: Dict[int, str],
                        word2id: Dict[str, int],
                        id2target: Dict[str, int],
                        WV: List[List[float]],
                        topk: int = 20):
    V = len(id2word)
    T = len(WV) // V
    logging.info(f"[calculate_neighbors] {V} words")
    logging.info(f"[calculate_neighbors] {T} time-bins")
    WV_eachtimes = np.split(WV, T)

    target_ids = list(id2target.keys())
    targetid2neighbors = {target_id: [] for target_id in target_ids}

    with open("/results/result_targetword_neighbors.tsv", "w") as fp:
        fp.write("target_word\tneighbors(distance)\n")

        for curr_time in range(T):
            logging.debug(f"[calculate_neighbors] - curr_time: {curr_time}")
            WV_curr = WV_eachtimes[curr_time]
            logging.debug(f"[calculate_neighbors]   - WV_curr: {WV_curr.shape}")
            WV_curr_targets = WV_curr[target_ids]
            logging.debug(f"[calculate_neighbors]   - WV_curr_targets: {WV_curr_targets.shape}")

            pdist_curr = cdist(WV_curr_targets, WV_curr)
            logging.debug(f"[calculate_neighbors]   - pair dist: {pdist_curr.shape}")

            for pdist_id, target_id in enumerate(target_ids):
                pdist_curr_each = pdist_curr[pdist_id]
                target_word = id2word[target_id]
                logging.debug(f"[calculate_neighbors]     - target_word: {target_word}") 
                neighbor_ids = [neighbor_id for neighbor_id in np.argsort(pdist_curr_each)[1:topk+1]]
                logging.debug(f"[calculate_neighbors]       - neighbor_ids: {neighbor_ids}") 
                neighbors = [f"{id2word[neighbor_id]}({pdist_curr_each[neighbor_id]:.4f})" for neighbor_id in neighbor_ids]
                logging.debug(f"[calculate_neighbors]       - neighbors: {neighbors}") 

                targetid2neighbors[target_id].append(", ".join(neighbors))

        for target_id in target_ids:
            neighbors_overtime: List[str] = targetid2neighbors[target_id]
            neighbors_tab_separated = "\t".join(neighbors_overtime)
            target_word = id2word[target_id]
            fp.write(f"{target_word}\t{neighbors_tab_separated}\n")


def cli_main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--pickle_id2word", help="path of dict[id]->word")
    parser.add_argument("--joint_vector", help="path of joint ppmi-svd vector matrix, (V*T, D) dim")
    parser.add_argument("--target_words", help="path of target words (\n separated, .txt style)")
    parser.add_argument("--topk", type=int, default=20, help="number of neighbors")

    args = parser.parse_args()

    id2word, word2id = load_pickle(args.pickle_id2word)
    WV = np.load(args.joint_vector)
    target_words = []
    with open(args.target_words) as fp:
        for line in fp:
            target_word = line.strip()
            target_words.append(target_word)

    id2target = get_target_ids(word2id, target_words)

    calculate_neighbors(id2word, word2id, id2target, WV, args.topk)


if __name__ == "__main__":
    cli_main()
