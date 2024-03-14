if [ $# -lt 4 ]; then
    echo "Missing arguments! Usage: <doc1> <doc2> ... <docN> <word_list> <thresh>"
    exit 1
fi


mkdir results
target_word_list=${@: -2:1}
target_word_list_abspath=$(readlink -f "$target_word_list")
target_word_list_filename=$(basename "$target_word_list")

document_commands=""
document_filepathes=""
for ((i = 1; i <= $# - 2; i++)); do
    document="${!i}"
    document_abspath=$(readlink -f "$document")
    document_filename=$(basename "$document")

    document_filepath="/data/${document_filename}"
    document_command="-v ${document_abspath}:${document_filepath}"
    document_commands="${document_commands} ${document_command}"

    document_filepathes="${document_filepathes} ${document_filepath}"

done

docker run --name ws-slim_container_prep \
    -w /app ${document_commands} \
    -v ./results:/results \
    ws-slim \
    python obtain_sharedvocab.py \
        --file_pathes ${document_filepathes} \
        --threshold ${!#} 

docker rm ws-slim_container_prep

docker run --name ws-slim_container_prep \
    -w /app \
    -v "${target_word_list_abspath}":/data/"${target_word_list_filename}" \
    -v ./results:/results \
    ws-slim \
    python add_targetwords_into_vocab.py \
        --pickle_id2word /results/id2word.pkl \
        --target_words /data/${target_word_list_filename}

docker remove ws-slim_container_prep

