# Template for litex projects

This project should serve as a template to launch litex projects.
It combines linux-on-litex and a generic litex project,
making it easier to bootstrap and launch litex projects.

## Dependencies

### OSS CAD suite

You'll need to install [oss-cad-suite](https://github.com/YosysHQ/oss-cad-suite-build).

#### IMPORTANT

Some FPGA boards (e. g. the digilent arty s7 with Vivado or the de10 nano with Alterra Quartus) may require their respective toolchains
for the bitstream to be built and programmed to the board. Make sure to install them.

Most boards could be built and flashed with just yosys+nextpnr+openocd, but do take care to check whether this would work with
your board or whether you would need another toolchain as well.

### Litex

Activate the environment for litex
```sh
source <path-to-oss-build>/environment
```

```sh
./install_litex.sh
```

Now, install all the system deps (this works on debian testing):

```sh
sudo apt install verilator libtool automake \
        pkg-config libusb-1.0-0-dev libjim-dev \
        default-jdk gcc-riscv64-unknown-elf device-tree-compiler
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

### The litex logic (Hardware)

Now that you've installed the requirements, you may build the app like so:

```
./hw/make.py --board <board name> --build --vexii-args <additional args>
```

To program the board, do

```
./hw/make.py --board <board name> --load
```

### The software

You may just cd into the project, like so

```
cd ./sw/<project name>
```

Then make

```
make
```

And program it with

```
lxterm /dev/ttyUSBN --kernel <program>.bin
```

Good luck!
