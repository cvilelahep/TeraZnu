FROM rootproject/root:6.38.00-ubuntu25.10

ENV DEBIAN_FRONTEND=noninteractive
ENV PREFIX=/opt/hep

# Core build tools + deps
RUN apt-get update && apt-get install -y \
    build-essential gfortran cmake git wget curl \
    python3 pkg-config \
    libgsl-dev libboost-all-dev \
    libssl-dev \
    autoconf automake libtool \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt
RUN mkdir -p $PREFIX

ENV PATH=$PREFIX/bin:$PATH
ENV LD_LIBRARY_PATH=$PREFIX/lib:$PREFIX/lib64:$LD_LIBRARY_PATH
ENV PKG_CONFIG_PATH=$PREFIX/lib/pkgconfig:$PREFIX/lib64/pkgconfig:$PKG_CONFIG_PATH

# ---------------------------
# LHAPDF
# ---------------------------
RUN wget https://lhapdf.hepforge.org/downloads/LHAPDF-6.5.5.tar.gz && \
    tar xf LHAPDF-6.5.5.tar.gz && cd LHAPDF-6.5.5 && \
    ./configure --prefix=$PREFIX && \
    make -j$(nproc) && make install

ENV LHAPDF_DATA_PATH=$PREFIX/share/LHAPDF

# Install a PDF set (optional but useful)
RUN lhapdf install cteq6l1 CT10

# ---------------------------
# HepMC3
# ---------------------------
RUN git clone https://gitlab.cern.ch/hepmc/HepMC3.git && \
    cd HepMC3 && mkdir build && cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=$PREFIX .. && \
    make -j$(nproc) && make install

# ---------------------------
# FastJet
# ---------------------------
RUN wget http://fastjet.fr/repo/fastjet-3.4.2.tar.gz && \
    tar xf fastjet-3.4.2.tar.gz && cd fastjet-3.4.2 && \
    ./configure --prefix=$PREFIX && \
    make -j$(nproc) && make install

# ---------------------------
# Pythia8
# ---------------------------
RUN apt-get update
RUN apt-get install -y rsync
RUN wget https://pythia.org/download/pythia83/pythia8309.tgz && \
    tar xf pythia8309.tgz && cd pythia8309 && \
    ./configure --prefix=$PREFIX \
        --with-hepmc3=$PREFIX \
        --with-lhapdf6=$PREFIX && \
    make -j$(nproc) && make install

# ---------------------------
# OpenLoops
# ---------------------------
RUN git clone https://gitlab.com/openloops/OpenLoops.git && \
    cd OpenLoops && \
    ./scons -j$(nproc)
RUN cd OpenLoops && \
    ./openloops libinstall ppllj eett tbw compile_extra=1 && \
    ./openloops update
ENV OPENLOOPS=/opt/OpenLoops
ENV PATH=$OPENLOOPS:$PATH

# ---------------------------
# WHIZARD 3.1.8
# ---------------------------
RUN ls $PREFIX
RUN apt-get install -y ocaml
RUN apt-get install -y libtirpc-dev
ENV PYTHONPATH=$PREFIX/lib/python3.13/dist-packages/lhapdf/:$PYTHONPATH
RUN lhapdf --listdir $LHAPDF_DATA_PATH update
RUN lhapdf --listdir $LHAPDF_DATA_PATH --pdfdir $LHAPDF_DATA_PATH install cteq6l1 CT10
RUN cd /opt/OpenLoops/ && openloops libinstall ppllj eett tbw compile_extra=1
RUN wget https://whizard.hepforge.org/downloads/whizard-3.1.8.tar.gz && \
    tar xf whizard-3.1.8.tar.gz && cd whizard-3.1.8 && \
    ./configure --prefix=$PREFIX \
        --with-lhapdf=$PREFIX \
        --with-hepmc=$PREFIX \
	--enable-pythia8 \
        --with-pythia8=$PREFIX \
	--enable-fastjet \
        --with-fastjet=$PREFIX \
	--enable-openloops \ 
        --with-openloops=$OPENLOOPS && \
    make -j$(nproc) && make install

WORKDIR /workspace

CMD ["bash"]