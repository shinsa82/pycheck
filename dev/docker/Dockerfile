FROM python:3.9

# RUN useradd -m -s /bin/bash -u 1001 user1
ENV VIRTUAL_ENV=/opt/venv
WORKDIR /root

# RUN ls -l /opt

# RUN chown 1001:1001 /opt
# USER 1001:1001
RUN mkdir .ssh
COPY ./github_ibm .ssh/

# RUN echo '${HOME}'
# RUN printenv

RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
ENV GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no -i .ssh/github_ibm"

# Install dependencies:
RUN pip install git+ssh://git@github.ibm.com/SHINSA/pycheck.git@dev

WORKDIR /app
