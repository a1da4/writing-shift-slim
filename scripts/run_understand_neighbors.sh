if [ $# -lt 3 ]; then
    echo "Missing arguments! Usage: <joint_vector> <word_list> <topk>"
    echo " <joint_vector>: please check ./results/models/ directory"
    exit 1
fi


joint_vector=${@: -3:1}
joint_vector_filename=$(basename "$joint_vector")
target_word_list=${@: -2:1}
target_word_list_abspath=$(readlink -f "$target_word_list")
target_word_list_filename=$(basename "$target_word_list")
topk=${@: -1:1}

docker run --name ws-slim_container_understand \
    -w /app \
    -v ./results:/results \
    -v "${target_word_list_abspath}":/data/"${target_word_list_filename}" \
    ws-slim \
    python calculate_neighbors.py \
        --pickle_id2word /results/id2word.pkl \
        --joint_vector /results/models/${joint_vector_filename} \
        --target_words /data/${target_word_list_filename} \
        --topk 20

docker remove ws-slim_container_understand

