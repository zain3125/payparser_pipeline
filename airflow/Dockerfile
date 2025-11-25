FROM apache/airflow:2.10.5
RUN pip install azure-cognitiveservices-vision-computervision
RUN pip install openpyxl
RUN pip install psycopg2-binary
ENV PYTHONPATH="/opt/airflow/app:${PYTHONPATH}"
