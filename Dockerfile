FROM python:3.9-alpine
LABEL authors="yao qi"
WORKDIR /app
COPY . .
RUN chmod -R +x bin && \
    pip3 install --no-cache-dir -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/
CMD [ "python3","-u","main.py" ]