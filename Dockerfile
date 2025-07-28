FROM registry.astralinux.ru/library/alse:latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-pip \
    g++ \
    make \
    cmake \
    libqt5widgets5 \
    libqt5gui5 \
    libqt5core5a \
    qtbase5-dev \
    qttools5-dev \
    qttools5-dev-tools \
    libpq-dev \
    python3-dev

COPY requirements.txt .
RUN pip3 install setuptools
RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . .

RUN chmod +x ./main.py
CMD ["python3", "./main.py"]
