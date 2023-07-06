FROM python:3.10.11 as base

ADD requirements.txt .
RUN pip3 install -r requirements.txt

ENV PYTHONPATH=$PYTHONPATH:/src

#COPY --chown=app:app . /src
COPY . /data_preloader
WORKDIR /data_preloader/src


FROM base as test
RUN ["pytest", "-v", "/src/tests"]

FROM base as build
ENTRYPOINT ["python3", "/data_preloader/src/main.py"]

