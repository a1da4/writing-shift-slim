if [ $# -lt 3 ]; then
    echo "Missing arguments! Usage: <doc1> <doc2> ... <word_list>"
    exit 1
fi

target_word_list="${!#}"
target_word_list_abspath=$(readlink -f "$target_word_list")
target_word_list_filename=$(basename "$target_word_list")

for ((i = 1; i <= $# - 1; i++)); do
    document="${!i}"
    document_abspath=$(readlink -f "$document")
    document_filename=$(basename "$document")
    echo "processing...: $document_filename"

    docker run --name writing_shift_py \
        -w /app -v "${document_abspath}":/data/"${document_filename}" \
        -v "${target_word_list_abspath}":/data/"${target_word_list_filename}" \
        ws-slim/v0 \
        python check_target_frequency.py \
            --file_pathes /data/$document_filename \
            --target_words /data/$target_word_list_file
    docker remove writing_shift_py

done

