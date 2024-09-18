# Dockerfile
FROM openjdk:8-jdk

# Set environment variables for Spark and Hadoop
ENV SPARK_VERSION=3.4.0 \
    HADOOP_VERSION=3 \
    PYSPARK_PYTHON=python3 \
    PYSPARK_DRIVER_PYTHON=python3

# Install necessary tools and Python
RUN apt-get update && \
    apt-get install -y curl python3 python3-pip && \
    pip3 install pyspark

# Download and install Spark
RUN curl -L --silent "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" | tar xz -C /opt && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark

# Set environment variables for Spark
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH

# Expose Spark ports
EXPOSE 8080 7077 6066 8081

# Copy entrypoint script to the container
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
