FROM tiangolo/uvicorn-gunicorn:python3.10 as base

RUN mkdir -p /fastapi /fastapi/embeddings /fastapi/static/templates/lib /fastapi/static/templates/js /fastapi/static/templates/contactform /fastapi/static/templates/img

ENV PYTHONPATH=$PYTHONPATH:/fastapi 

COPY requirements.txt /fastapi 

WORKDIR /fastapi

RUN pip install -r requirements.txt

COPY . /fastapi

EXPOSE 8000

FROM base as test
RUN ["pytest", "-v", "/fastapi/tests"]

FROM base as build
ENTRYPOINT ["uvicorn", "--workers=8","--host","0.0.0.0","--port","8000","app:app"]
