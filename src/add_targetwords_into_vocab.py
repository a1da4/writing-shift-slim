import argparse
import pickle
import logging

from typing import Dict, List

from sppmisvd.util import load_pickle


def add_targetwords_into_vocab(id2word: Dict[int, str], word2id: Dict[str, int], 
                               target_words: List[str]):
    curr_id = len(id2word)
    for target_word in target_words:
        if target_word not in word2id:
            id2word[curr_id] = target_word
            curr_id += 1
            logging.info(f"[add_targetwords_into_vocab] add {target_word}")

    pickle.dump(id2word, open("id2word.pkl", "wb"))


def cli_main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--pickle_id2word", help="path of dict[id]->word")
    parser.add_argument("--target_words", help="path of target words (\n separated, .txt style)")

    args = parser.parse_args()

    target_words = []
    with open(args.target_words) as fp:
        for line in fp:
            target_word = line.strip()
            target_words.append(target_word)

    id2word, word2id = load_pickle(args.pickle_id2word)

    add_targetwords_into_vocab(id2word, word2id, target_words)


if __name__ == "__main__":
    cli_main()
