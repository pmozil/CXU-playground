# Template for litex projects

This project should serve as a template to launch litex projects.
It combines linux-on-litex and a generic litex project,
making it easier to bootstrap and launch litex projects.

## Dependencies

### OSS CD suite

You'll need to install [oss-cad-suite](https://github.com/YosysHQ/oss-cad-suite-build).


### Litex

Activate the environment for litex
```sh
source <path-to-oss-build>/environment
```

```sh
mkdir -p litex && cd litex
wget https://raw.githubusercontent.com/enjoy-digital/litex/master/litex_setup.py
chmod +x litex_setup.py
./litex_setup.py --init --install --user
```

Now, install all the system deps (this works on debian testing):

```sh
sudo apt install verilator libtool automake \
        pkg-config libusb-1.0-0-dev \
        default-jdk gcc-riscv64-unknown-elf
```

### OpenOCD
```sh
git clone https://github.com/ntfreak/openocd.git
cd openocd
./bootstrap
./configure --enable-ftdi
make
sudo make install
```

### Build tools

Activate the OSS CAD Suite env
```sh
source <path-to-oss-build>/environment
```

```sh
pip3 install meson ninja
```

### SBT

```sh
sudo apt-get update
sudo apt-get install apt-transport-https curl gnupg -yqq
echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | sudo tee /etc/apt/sources.list.d/sbt.list
echo "deb https://repo.scala-sbt.org/scalasbt/debian /" | sudo tee /etc/apt/sources.list.d/sbt_old.list
curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | sudo -H gpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/scalasbt-release.gpg --import
sudo chmod 644 /etc/apt/trusted.gpg.d/scalasbt-release.gpg
sudo apt-get update
sudo apt-get install sbt
```


## Usage
