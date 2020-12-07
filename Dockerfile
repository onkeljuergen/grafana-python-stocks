FROM python:3.8

RUN pip install psycopg2 flask flask-jsonpify flask-sqlalchemy flask-restful flask-apscheduler ptvsd influxdb
RUN pip install yfinance --upgrade --no-cache-dir
RUN pip install requests_html yahoo_fin

EXPOSE 8000
EXPOSE 5000

COPY ./app /app

CMD python  /app/app.py