FROM python:3.10-slim-buster

WORKDIR /secrets_shaman

COPY . /secrets_shaman

RUN pip3 install --no-cache-dir -r ./app/requirements.txt

RUN groupadd -r shaman && useradd -r -g shaman shaman
RUN chown -R shaman:shaman /secrets_shaman
USER shaman

CMD ["python3", "./app/main.py" ]