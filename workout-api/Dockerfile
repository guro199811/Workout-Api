FROM python:3.10.2

# Setting working directory
WORKDIR /code


COPY ./requirements.txt /code/requirements.txt


# Installing dependencies using python package installer
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code


COPY . /code/

RUN chmod +x /code/entrypoint.sh

ENTRYPOINT ["/code/entrypoint.sh"]