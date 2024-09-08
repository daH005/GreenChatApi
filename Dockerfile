FROM python:3.11

COPY ./* /api
WORKDIR /api

RUN apt update
RUN pip3 install -r requirements.txt

ENV PYTHONPATH=/api

CMD ["python3", "main.py"]
