FROM surnet/alpine-wkhtmltopdf:3.22.0-0.12.6-full AS wkhtmltopdf
FROM python:3.12-alpine3.21


# Install dependencies
RUN apk add --no-cache \
    libstdc++ \
    libx11 \
    libxrender \
    libxext \
    libssl3 \
    ca-certificates \
    fontconfig \
    freetype \
    ttf-dejavu \
    ttf-droid \
    ttf-freefont \
    ttf-liberation \
    build-base \
    postgresql-dev \
    gcc \
    openssl-dev \
    openssl \
    curl \
    sqlite-libs>=3.40.1-r0 \
    # more fonts
    && apk add --no-cache --virtual .build-deps \
    msttcorefonts-installer \
    # Install microsoft fonts
    && update-ms-fonts \
    && fc-cache -f \
    # Clean up when done
    && rm -rf /tmp/* \
    && apk del .build-deps

# Copy wkhtmltopdf files from docker-wkhtmltopdf image
COPY --from=wkhtmltopdf /bin/wkhtmltopdf /bin/wkhtmltopdf
COPY --from=wkhtmltopdf /bin/wkhtmltoimage /bin/wkhtmltoimage
COPY --from=wkhtmltopdf /bin/libwkhtmltox* /bin/

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install wheel>=0.38.4 && pip install -r requirements.txt

ADD ./ .

ENV PYTHONPATH=""
ENV PYTHONPATH="${PYTHONPATH}:/app"

RUN addgroup \
    --gid 1000 \
    -S solarpark-service
RUN adduser \
    --uid 1000 \
    -G solarpark-service \
    -S solarpark-service

USER solarpark-service

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]