FROM python:3.10.2

# Setting working directory
WORKDIR /workout-api


# Dependencies
COPY ./requirements.txt ./requirements.txt

# Installing dependencies using python package installer
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code


COPY ./workout-api/ /workout-api/

ENV PYTHONPATH=/workout_api

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


