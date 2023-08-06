FROM python:3.10-slim

ARG VERSION
ARG TF_VERSION=1.1.5

ENV TF_INPUT false
ENV TF_CLI_ARGS -no-color
ENV PYTHONUNBUFFERED true

RUN apt-get update -y && apt-get install -y git wget unzip curl gnupg

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
    && apt-get update -y && apt-get install google-cloud-cli -y
      
RUN wget https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip \
    && unzip terraform_${TF_VERSION}_linux_amd64.zip \
    && mv terraform /usr/local/bin/ \
    && rm terraform_${TF_VERSION}_linux_amd64.zip

RUN pip install mwg-cli==$VERSION

ENTRYPOINT ["mwg"]