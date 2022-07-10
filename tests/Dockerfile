FROM python:3.8-slim

WORKDIR /
COPY tests/requirements.txt ./
RUN pip install -r requirements.txt
RUN rm requirements.txt

WORKDIR /tes_reader
COPY /tes_reader/*.py ./

WORKDIR /tests
COPY tests/*.py ./
RUN echo [Skyrim] > test.ini
RUN echo >> test.ini
RUN echo "Folder = /skyrim/" >> test.ini

CMD ["py.test"]