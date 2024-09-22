FROM python:3
WORKDIR /image_outline
COPY . /image_outline
RUN pip install -r requirements.txt
EXPOSE 3000
# CMD python ./main.py
CMD ["python", "main.py"]