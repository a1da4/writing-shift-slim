if [ $# -lt 3 ]; then
    echo "Missing arguments! Usage: <doc1> <doc2> ... <docN> <word_list>"
    exit 1
fi

mkdir results

target_word_list="${!#}"
target_word_list_abspath=$(readlink -f "$target_word_list")
target_word_list_filename=$(basename "$target_word_list")

document_commands=""
document_filepathes=""
for ((i = 1; i <= $# - 1; i++)); do
    document="${!i}"
    document_abspath=$(readlink -f "$document")
    document_filename=$(basename "$document")

    document_filepath="/data/${document_filename}"
    document_command="-v ${document_abspath}:${document_filepath}"
    document_commands="${document_commands} ${document_command}"

    document_filepathes="${document_filepathes} ${document_filepath}"

done

docker run --name ws-slim_container_check \
    -w /app ${document_commands} \
    -v "${target_word_list_abspath}":/data/"${target_word_list_filename}" \
    -v ./results:/results \
    ws-slim \
    python check_target_frequency.py \
        --file_pathes ${document_filepathes} \
        --target_words /data/${target_word_list_filename}

docker remove ws-slim_container_check

