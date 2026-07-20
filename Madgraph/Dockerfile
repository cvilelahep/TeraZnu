# Dockerfile for MadGraph5_aMC@NLO v3.7.2 + LHAPDF6 + Pythia8
FROM ubuntu:25.10

ENV DEBIAN_FRONTEND=noninteractive
ENV MG_VERSION=3.7.2
ENV MG_DIR=/opt/MG5_aMC_v3_7_2

# --- System dependencies ---
# Added: libboost-dev (Pythia8/HepMC often need it), autoconf/libtool
# (some MG5-managed installs of LHAPDF/HepMC build via autotools),
# and rsync (used by some MG5 install scripts to fetch/copy files)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gfortran \
    gcc \
    g++ \
    make \
    cmake \
    wget \
    curl \
    ca-certificates \
    tar \
    git \
    rsync \
    autoconf \
    automake \
    libtool \
    libboost-dev \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    libz-dev \
    libbz2-dev \
    vim \
    less \
    bc \
    && rm -rf /var/lib/apt/lists/*

# PEP 668 override for Ubuntu 25.10's Python 3.13
RUN pip3 install --no-cache-dir --break-system-packages \
    numpy \
    scipy \
    matplotlib \
    six

WORKDIR /opt

# --- Download and unpack MadGraph5_aMC@NLO v3.7.0 ---
RUN wget -q https://launchpad.net/mg5amcnlo/3.0/3.7.x/+download/MG5_aMC_v${MG_VERSION}.tar.gz \
    && tar -xzf MG5_aMC_v${MG_VERSION}.tar.gz \
    && rm MG5_aMC_v${MG_VERSION}.tar.gz

WORKDIR ${MG_DIR}

# --- Smoke-test generation+compile to force Fortran toolchain check ---
RUN echo "generate e+ e- > mu+ mu-" > /tmp/mg5_test.mg5 \
    && echo "output /tmp/test_proc" >> /tmp/mg5_test.mg5 \
    && python3 ./bin/mg5_aMC /tmp/mg5_test.mg5 \
    && cd /tmp/test_proc \
    && make -C Source \
    && rm -rf /tmp/test_proc /tmp/mg5_test.mg5

# --- Install LHAPDF6 and Pythia8 via MG5's internal installer ---
# MG5's `install` command downloads sources into ${MG_DIR}/HEPTools and builds
# them, then wires up config entries in input/mg5_configuration.txt so that
# subsequent process generation/showering automatically finds them.
# This step can take a long time (Pythia8 build especially) and needs network
# access at build time — make sure your build environment allows it.
RUN echo "install lhapdf6" > /tmp/mg5_install.mg5 \
    && echo "install pythia8" >> /tmp/mg5_install.mg5 \
    && python3 ./bin/mg5_aMC /tmp/mg5_install.mg5 \
    && rm -f /tmp/mg5_install.mg5
    
# Make sure LHAPDF's own CLI tools (lhapdf-config etc.) and shared libs are
# discoverable outside of MG5-managed process directories too
ENV LHAPDF_DIR=${MG_DIR}/HEPTools/lhapdf6
ENV PYTHIA8_DIR=${MG_DIR}/HEPTools/pythia8
ENV PATH="${MG_DIR}/bin:${LHAPDF_DIR}/bin:${PYTHIA8_DIR}/bin:${PATH}"
ENV LD_LIBRARY_PATH="${LHAPDF_DIR}/lib:${PYTHIA8_DIR}/lib:${LD_LIBRARY_PATH}"
ENV PYTHONPATH="${LHAPDF_DIR}/lib/python3.13/site-packages:${PYTHONPATH}"

WORKDIR ${MG_DIR}

CMD