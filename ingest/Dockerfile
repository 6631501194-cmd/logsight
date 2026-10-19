FROM python:3.12-alpine
WORKDIR /app
COPY syslog_collector.py .
EXPOSE 5514/udp
CMD ["python", "syslog_collector.py"]
