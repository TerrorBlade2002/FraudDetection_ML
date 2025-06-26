FROM python:3.10.16-slim-bookworm
WORKDIR /app
COPY requirements.txt /app/requirements.txt

#slim-bookworm -> to save space (lightweight python image)
# Install dependencies
RUN pip install -r /app/requirements.txt

# Copy the rest of the application
COPY . .

# Set the command to run your application (expose it to port 5500)
EXPOSE 5500