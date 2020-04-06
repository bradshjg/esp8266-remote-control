FROM python:alpine as base

WORKDIR /src

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#-----------------------------------------------------------------------------

FROM base as test

COPY test-requirements.txt .

RUN pip install --no-cache-dir -r test-requirements.txt

#-----------------------------------------------------------------------------

FROM base as prod

COPY deploy-requirements.txt .

RUN pip install --no-cache-dir -r deploy-requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input

# FIXME we need to override the command when we're ready to deploy
