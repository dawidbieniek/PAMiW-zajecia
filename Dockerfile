FROM python:3.8-slim-buster
WORKDIR /var/www
ENV FLASK_APP app/start.py
ENV FLASK_DEBUG 1
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 5050
COPY requirements.txt require.txt
RUN pip install -r require.txt
COPY . .
CMD ["flask", "run"]
