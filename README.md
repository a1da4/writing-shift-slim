#writing-shift-slim
light-weight implementation of 'writing-shift' https://github.com/a1da4/writing-shift

## Setup
```
docker build -t ws-slim .
```

## Preprocess
Check target word frequencies
```
cd scripts/

bash run_check_target_frequency.sh <doc1> <doc2> ... <docN> <target_word_list>

bash run_preprocess.sh <doc1> <doc2> ... <docN> <target_word_list> <threshold>
```
