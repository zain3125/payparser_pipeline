FROM apache/airflow:2.10.5

COPY requirements.txt /

RUN PYV=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')") \
    && pip install --no-cache-dir -r /requirements.txt \
       --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-${PYV}.txt"

ENV PYTHONPATH="/opt/airflow/app:${PYTHONPATH}"

USER airflow
