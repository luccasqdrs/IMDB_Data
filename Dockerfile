FROM python:3.5-jessie


RUN apt-get update

WORKDIR /root
RUN mkdir imdb_data
COPY ./ ./imdb_data/
COPY ./python/* ./imdb_data/
RUN pip install -qr ./imdb_data/requirements.txt

ENTRYPOINT ["python", "./imdb_data/crawler.py"]
EXPOSE 5000
