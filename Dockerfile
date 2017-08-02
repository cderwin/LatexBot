FROM python:3.6

RUN apt update && \
    apt install -y texlive-latex-extra texlive-math-extra ghostscript imagemagick

RUN mkdir /code
WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "/code/latexbot.py"]
