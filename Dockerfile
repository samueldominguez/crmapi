
FROM python:3.8.9 as base
RUN mkdir -p /var/www/crmapi
WORKDIR /var/www/crmapi
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

FROM base as dev
ENV ENV DEV
ENV PYTHONDONTWRITEBYTECODE 1

FROM base as prod
ENV ENV PROD
RUN ["flask", "--app", "app", "init-db"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:create_app()", "--log-level debug"]