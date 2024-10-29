FROM continuumio/miniconda3

COPY requirements.txt .

RUN apt-get update \ 
    && apt-get -y install g++ gcc libsm6 libxext6 cron pciutils libgl1-mesa-glx

RUN apt -y install default-jre
RUN apt-get update && apt-get install -y openjdk-17-jdk && apt-get clean;
RUN pip install -r requirements.txt

COPY src src
COPY main.py main.py

EXPOSE 8000 8501

CMD  python main.py