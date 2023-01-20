FROM python:3.8-slim-buster
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP app/start.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 5050
COPY ../docker/main/required.txt required.txt
RUN apt-get update && apt-get install -y
RUN apt-get install libzbar0 -y
RUN pip install -r required.txt
COPY ./app ./app
COPY ./db/database.db ./db/database.db
CMD ["flask", "run"]