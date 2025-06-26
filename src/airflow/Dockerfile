FROM apache/airflow:2.10.5

#Create models dictionary and set ownership
USER root
RUN mkdir -p /app/models

USER airflow

#Copy requirements file
COPY requirements.txt /tmp/requirements.txt

#Install Python pkgs as root (system-wide)
RUN pip install -r /tmp/requirements.txt

#Switch back to user airflow for safety
USER airflow
