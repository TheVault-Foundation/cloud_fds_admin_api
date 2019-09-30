FROM python:3.7-alpine as builder

RUN mkdir /install
WORKDIR /install

RUN apk --no-cache add g++ make openssl-dev libffi-dev \
    && pip install pipenv

COPY Pipfile* ./

RUN pipenv lock -r > requirements.txt \
    && pip install --prefix=/install --ignore-installed -r requirements.txt


FROM python:3.7-alpine

RUN adduser -D adminapi

WORKDIR /home/adminapi
COPY --from=builder /install /usr/local
COPY app/ app/
COPY entry-point.sh .
COPY manage.py manage.py

USER adminapi

EXPOSE 5000

ENTRYPOINT ["./entry-point.sh"]
