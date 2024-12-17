FROM py312

RUN apt-get update -y || true && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libgstreamer1.0-dev \
    gstreamer1.0-plugins-base-apps \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    gstreamer1.0-rtsp \
    gstreamer1.0-plugins-ugly \
    gir1.2-gst-plugins-base-1.0 \
    gir1.2-gstreamer-1.0 \
    libcairo2-dev \
    libgirepository1.0-dev \
    python3-gst-1.0

RUN pip install pycairo PyGObject
RUN pip install gst-python-stubs==0.0.2
RUN pip install PyGObject-stubs==2.12.0
RUN pip install opencv-python==4.8.0.74