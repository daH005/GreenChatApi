FROM python:3.11

RUN useradd -m user

WORKDIR /home/user/api
COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

USER user
COPY --chown=user:user . .

CMD ["python3", "main.py"]
