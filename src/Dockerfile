FROM python:3.9.7-slim

# install psycopg2 dependencies
RUN apt update && apt install libpq-dev gcc -y -q

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV APP_HOME=/django
ENV ENTRYPOINT="entrypoint.sh"
ENV ENTRYPOINT_DIR="${APP_HOME}/${ENTRYPOINT}"

WORKDIR $APP_HOME

# install dependencies
ADD poetry.lock pyproject.toml ./

RUN pip install --upgrade pip poetry --no-cache
RUN poetry config virtualenvs.in-project true
RUN poetry install

# copy entrypoint.sh
ADD ./${ENTRYPOINT} .
RUN sed -i 's/\r$//g' ${ENTRYPOINT_DIR}
RUN chmod +x ${ENTRYPOINT_DIR}

# copy project
COPY . $APP_HOME

# run entrypoint
ENTRYPOINT ["/django/entrypoint.sh"]