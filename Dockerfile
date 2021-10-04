FROM python:3.8
COPY ./lottery_system /app
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
WORKDIR /app
EXPOSE 8080
CMD ["gunicorn", "--conf", "/app/config/gunicorn_conf.py", "--bind", "0.0.0.0:8080", "main:app", "--worker-class", "gevent"]
