#!/bin/bash

FILE="locust/fuzzing.txt"

while IFS= read -r payload; do
    # pomijamy puste linie
    [ -z "$payload" ] && continue

    echo "Request: /$payload"
    curl "http://localhost:5555/$payload"
    echo -e "\n---"
done < "$FILE"