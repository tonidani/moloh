FROM ubuntu:latest

# Instalacja zależności i Ollama
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://ollama.com/install.sh | sh

# Skopiuj skrypt startowy
COPY start.sh /tmp/start.sh
RUN chmod +x /tmp/start.sh

CMD ["sh", "/tmp/start.sh"]