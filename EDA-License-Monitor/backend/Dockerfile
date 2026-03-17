FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# FlexLM (Synopsys lmutil) binary expects /lib64/ld-lsb-x86-64.so.3 on some distros.
# Keep a compatible linker alias so lmutil stays executable after container rebuilds.
RUN mkdir -p /lib64 && ln -sf /lib64/ld-linux-x86-64.so.2 /lib64/ld-lsb-x86-64.so.3

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
