FROM python:3.11

COPY ./build/python/requirements.txt ./

RUN echo "umask 0022" >> /etc/profile

RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/; \
sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources ; apt update; \
echo complete;

