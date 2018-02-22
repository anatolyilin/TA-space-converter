# TA-space-converter

removes spaces in files within TA course modules. 

To build:

docker build -t TA-space-conv:latest .

To run:

docker run -d -p 5000:5000 --restart unless-stopped TA-space-conv
