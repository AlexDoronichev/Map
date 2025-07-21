FROM registry.astralinux.ru/library/alse:latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    g++ \
    make \
    cmake \
    libqt5widgets5 \
    libqt5gui5 \
    libqt5core5a \
    libqt5network5 \
    qtbase5-dev \
    qttools5-dev \
    qttools5-dev-tools

WORKDIR /app
COPY . .

RUN qmake
RUN make

RUN chmod +x ./my-app
CMD ["./my-app"]
