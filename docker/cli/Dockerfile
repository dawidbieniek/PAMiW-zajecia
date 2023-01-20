FROM python:3.8-slim-buster
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP cli/start.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 5000
COPY ../docker/cli/required.txt required.txt
RUN apt-get update && apt-get install -y
RUN apt-get install libzbar0 -y
RUN pip install -r required.txt
COPY ./cli ./cli
COPY ./app/rpc.py ./cli/rpc.py
COPY ./app/qr.py ./cli/qr.py
CMD ["flask", "run"]