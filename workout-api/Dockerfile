FROM python:3.10.2

# Setting working directory
WORKDIR /app

# Copy your application code
COPY . .

# Installing dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 5000

# Running uvicorn to start the FastAPI application
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" ]
