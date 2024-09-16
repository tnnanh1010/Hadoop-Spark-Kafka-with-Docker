# Use an appropriate base image for Spark and Python
FROM bde2020/spark-python-template:2.4.5-hadoop2.7

# Copy your application files
COPY . /app

# Ensure the run.sh script is executable
RUN chmod +x /app/run.sh

# Set the working directory
WORKDIR /app

# Automatically execute the run.sh script
CMD ["/app/run.sh"]
