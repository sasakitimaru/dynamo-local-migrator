FROM python:3.6

RUN apt-get update && apt-get install less

RUN mkdir -p /root/.local/bin
ENV PATH $PATH:/root/.local/bin

RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        AWS_CLI_URL="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        AWS_CLI_URL="https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip"; \
    else \
        echo "Unsupported architecture: $ARCH"; \
        exit 1; \
    fi && \
    curl "$AWS_CLI_URL" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

RUN pip install pyyaml

WORKDIR /home/dynamodblocal

COPY ./src/ /home/dynamodblocal/
COPY ./schema/ /home/dynamodblocal/schema/

CMD ["python3", "init_dynamodb.py"]