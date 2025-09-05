# Stage 1: hämta wkhtmltopdf
FROM surnet/alpine-wkhtmltopdf:3.22.0-0.12.6-full AS wkhtmltopdf

# Stage 2: Python-app
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
    curl \
    sqlite-libs \
    postgresql-dev \
    && apk add --no-cache --virtual .build-deps \
       build-base gcc musl-dev openssl-dev msttcorefonts-installer \
    && update-ms-fonts && fc-cache -f \
    && apk del .build-deps \
    && rm -rf /tmp/*

# Kopiera wkhtmltopdf-binärer från stage 1
COPY --from=wkhtmltopdf /bin/wkhtmltopdf /bin/
COPY --from=wkhtmltopdf /bin/wkhtmltoimage /bin/
COPY --from=wkhtmltopdf /bin/libwkhtmltox* /bin/

# Arbetskatalog
WORKDIR /app

# Installera Python-dependencies först (bättre caching)
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install "wheel>=0.38.4" \
 && pip install --no-cache-dir -r requirements.txt

# Kopiera in all kod
COPY . .

# Miljövariabler
ENV PYTHONPATH=/app

# Skapa icke-root-användare
RUN addgroup -S solarpark-service -g 1000 \
 && adduser -S solarpark-service -u 1000 -G solarpark-service

USER solarpark-service

# Startkommando
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
