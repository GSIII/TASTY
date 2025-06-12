# Step 1 : Base Images
FROM python:3.9

# Step 2 : Package Install
RUN apt -y update; apt -y upgrade; apt -y install vim git net-tools

# Step 3 : Specify a Working directory
WORKDIR /root

# Step 4 : Config file copy
COPY ai/ .
RUN pip install -r requirements.txt

# Step 5 : Open port
EXPOSE 8501

# Step 6 : Execution Program
CMD ["streamlit","run","app.py"]