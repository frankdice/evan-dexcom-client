FROM tiangolo/uwsgi-nginx-flask:python3.12-2025-06-16

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./ /app