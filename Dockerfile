FROM python:3.7-slim

RUN mkdir -m 777 -p /source/spam_monitor_system
ADD requirements.txt /source/spam_monitor_system
RUN pip install -r /source/spam_monitor_system/requirements.txt

ADD ./ /source/spam_monitor_system
WORKDIR /source/spam_monitor_system
RUN chmod 777 ./scripts/run_service.sh
RUN chmod 777 ./scripts/run_all_tests.sh
RUN chmod 777 ./scripts/run_integration_tests.sh
RUN chmod 777 ./scripts/wait_for_it.sh