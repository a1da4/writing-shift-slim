import argparse
import logging
import os
import pickle

import numpy as np
from scipy.spatial.distance import euclidean
from typing import Dict, List

from sppmisvd.util import load_pickle


def calculate_distance_targets(id2word: Dict[int, str],
                               word2id: Dict[str, int],
                               target_words: List[str],
                               WV: List[List[float]],
                               output: str = "test") -> None:

    os.makedirs("/results/distances", exist_ok=True)
    V = len(id2word)
    T = len(WV) // V
    WV_eachtimes = np.split(WV, T)

    target2results = {}
    for target_word in target_words:
        target2results[target_word] = []
        for curr_time in range(T):
            results_currtime = []
            target_id = word2id[target_word]
            target_vec = WV_eachtimes[curr_time][target_id]
            if curr_time < T - 1:
                next_vec = WV_eachtimes[curr_time+1][target_id]
                distance = euclidean(target_vec, next_vec)
                results_currtime.append(f"{target_word}[{curr_time+1}]({distance:.4f})")
            for reference_word in target_words:
                if reference_word == target_word:
                    continue
                reference_id = word2id[reference_word]
                reference_vec = WV_eachtimes[curr_time][reference_id]
                distance = euclidean(target_vec, reference_vec)
                results_currtime.append(f"{reference_word}({distance:.4f})")
            result_currtime = ",".join(results_currtime)
            target2results[target_word].append(result_currtime)

    with open(f"/results/distances/{output}.tsv", "w") as fp:
        timeslices = "\t".join([str(t) for t in range(T)])
        fp.write(f"target_word\t{timeslices}\n")
        for target_word in target_words:
            results_eachtimes = target2results[target_word]
            results_eachtimes_tabseparated = "\t".join(results_eachtimes)
            fp.write(f"{target_word}\t{results_eachtimes_tabseparated}\n")





def cli_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pickle_id2word", help="path of dict[id]->word")
    parser.add_argument("--joint_vector", help="path of joint ppmi-svd vector matrix, (V*T, D) dim")
    parser.add_argument("--target_word_pathes", nargs="*", help="pathes of target words (\n separated, .txt style)")
    parser.add_argument("--output_names", nargs="*", help="output names")

    args = parser.parse_args()

    id2word, word2id = load_pickle(args.pickle_id2word)
    WV = np.load(args.joint_vector)
    
    for target_word_path, output_name in zip(args.target_word_pathes, args.output_names):
        target_words = []
        with open(target_word_path) as fp:
            for line in fp:
                target_word = line.strip()
                target_words.append(target_word)
        
        calculate_distance_targets(id2word, word2id, target_words, WV, output_name)


if __name__ == "__main__":
    cli_main()
