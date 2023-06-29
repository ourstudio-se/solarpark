FROM python:3.10-alpine3.16

RUN apk update && \
    apk upgrade --no-cache && \
    apk add --no-cache \
    build-base postgresql-dev gcc openssl-dev openssl curl sqlite-libs>=3.40.1-r0 \

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install wheel>=0.38.4 && pip install -r requirements.txt

ADD ./ .

ENV PYTHONPATH "#{PYTHONPATH}:/app"


RUN addgroup \
    --gid 1000 \
    -S solarpark-service
RUN adduser \
    --uid 1000 \
    -G solarpark-service \
    -S solarpark-service

USER solarpark-service

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]