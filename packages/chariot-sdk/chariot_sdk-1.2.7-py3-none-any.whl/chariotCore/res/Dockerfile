FROM python:3.8-slim

WORKDIR /python/src
ADD . /python/src
RUN chmod +x /python/src/main.py

# replace apt source && config pip source
RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list && \
  sed -i "s@http://security.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list && \
  apt-get update && apt-get install -y iputils-ping net-tools vim && apt-get clean && \
  pip config set global.index-url https://mirrors.aliyun.com/pypi/simple && \
  /bin/echo -e [easy_install]\\nindex-url=https://mirrors.aliyun.com/pypi/simple > ~/.pydistutils.cfg

# Install pip dependencies
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

ENTRYPOINT ["/python/src/main.py"]