import argparse
import pickle
import logging

from collections import Counter

from typing import Dict, List


def main(file_pathes: List[str], target_words: List[str]) -> None:
    vocab = set(target_words)
    target2freqs = {}
    for target_word in target_words:
        target2freqs[target_word] = []

    for file_path in file_pathes:
        logging.info(f"[main] file_path: {file_path}")
        word2freq = Counter()
        with open(file_path) as fp:
            for line in fp:
                words = line.strip().split()
                for word in words:
                    if word not in vocab:
                        continue
                    word2freq[word] += 1
        for target_word in target_words:
            logging.info(f"[main]  - {target_word}\t{word2freq[target_word]}")
            target2freqs[target_word].append(str(word2freq[target_word]))

    with open("check_target_frequency.tsv", "w") as fp:
        fp.write("target\tfrequency\n")
        for target_word in target_words:
            frequency_tab_separated = "\t".join(target2freqs[target_word])
            fp.write(f"{target_word}\t{frequency_tab_separated}\n")



def cli_main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_pathes", nargs="*", help="path of a target file")
    parser.add_argument("--target_words", help="path of target words (\n separated, .txt style)")
    args = parser.parse_args()

    target_words = []
    with open(args.target_words) as fp:
        for line in fp:
            target_word = line.strip()
            target_words.append(target_word)

    main(args.file_pathes, target_words)


if __name__ == "__main__":
    cli_main()
