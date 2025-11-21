#!/bin/bash

# Uruchom serwer Ollama w tle
ollama serve &

# Zapisz PID procesu serwera
SERVER_PID=$!

# Funkcja do czyszczenia
cleanup() {
    kill $SERVER_PID
}
trap cleanup EXIT

# Poczekaj aż serwer będzie gotowy
echo "Waiting for Ollama server to start..."
while ! curl -s http://localhost:11434 > /dev/null; do
    sleep 1
done

# Jeśli określono model do pobrania, pobierz go
if [ -n "$DOWNLOAD_MODEL" ]; then
    echo "Pulling model: $DOWNLOAD_MODEL"
    ollama pull "$DOWNLOAD_MODEL" || {
        echo "Failed to pull model $DOWNLOAD_MODEL"
        exit 1
    }
    echo "Successfully pulled model: $DOWNLOAD_MODEL"
fi

# Czekaj na zakończenie pracy serwera
wait $SERVER_PID