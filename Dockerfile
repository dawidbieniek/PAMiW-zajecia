FROM python:3.8-slim-buster
WORKDIR /var/www
ENV FLASK_APP app/start.py
# ENV FLASK_DEBUG 1
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 5050
COPY required.txt required.txt
RUN pip install -r required.txt
COPY . .
# COPY app .
# COPY db .
CMD ["flask", "run"]
