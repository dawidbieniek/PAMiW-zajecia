FROM python:3.8-slim-buster
COPY ../docker/res/required.txt required.txt
RUN pip install -r required.txt
COPY ./res ./res
COPY ./db/databaseRes.db ./db/database.db
COPY ./app/mydb.py ./res/mydb.py
CMD ["python3", "./res/start.py"]