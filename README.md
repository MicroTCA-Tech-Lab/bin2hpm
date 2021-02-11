# bin2hpm

This is a tool that creates HPM.1 firmware update files to be used by a HPM.1 updater such as `ipmitool hpm upgrade`.

It can be used with [MMC-STAMP](https://techlab.desy.de/products/module_management_controller/mmc_stamp/index_eng.html) based AMC boards, such as the [DAMC-FMC2ZUP](https://techlab.desy.de/products/amc/damc_fmc2zup/index_eng.html) and [DAMC-FMC1Z7IO](https://techlab.desy.de/products/amc/damc_fmc1z7io/index_eng.html), to facilitate in-system-upgrade of various components (MMC, CPLDs, FPGAs) over IPMI.

## Features

* Converts from binary file to firmware update file according to HPM.1 spec
* Creates a sequence of two HPM.1 actions; first *Prepare component*, then *Upload image*
* Embeds metadata according to HPM.1 spec:
    * IANA manufacturer / product ID
    * Target device / component
    * Version information
    * Auxillary metadata
* Parses Xilinx bitstream file (optional)
* Performs RLE compression (optional / DESY MMC proprietary)

## File mode

By default, Xilinx bitfile mode is determined from the input file name. If it ends on `.bit`, the bitfile mode is selected. Bitfile mode can also be forced (`-b`) or suppressed (`-n`) independent of file name.

## Usage

```
$ bin2hpm --help
usage: bin2hpm [-h] [--version] [-o OUTFILE] [-v FILE_VERSION] [-a AUXILLARY] [-c COMPONENT] [-d DEVICE] [-m MANUFACTURER] [-p PRODUCT] [-r] [-s DESCRIPTION] [-b | -n] infile

HPM.1 update file converter

positional arguments:
  infile                Input file

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -o OUTFILE, --outfile OUTFILE
                        output file (derived from input file if not set)
  -v FILE_VERSION, --file-version FILE_VERSION
                        file version information (format major.minor, e.g. 1.2)
  -a AUXILLARY, --auxillary AUXILLARY
                        additional metadata, hex format, 4 bytes
  -c COMPONENT, --component COMPONENT
                        HPM component ID (default 1)
  -d DEVICE, --device DEVICE
                        HPM device ID (hex, default 0)
  -m MANUFACTURER, --manufacturer MANUFACTURER
                        IANA manufacturer ID (hex, 6 bytes max)
  -p PRODUCT, --product PRODUCT
                        IANA product ID (hex, 4 bytes max)
  -r, --compress        Enable RLE compression (requires DESY MMC)
  -s DESCRIPTION, --description DESCRIPTION
                        Additional description string (max. 21 chars)
  -b, --bitfile         Force bitfile mode
  -n, --binfile         Force binfile mode
```