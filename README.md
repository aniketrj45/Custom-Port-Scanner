# Custom Port Scanner

A tool for scanning ports on a target host to assess whether they are open or closed.

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Architecture](#architecture)
6. [Contributing](#contributing)
7. [License](#license)

## Introduction
This Custom Port Scanner allows users to detect open ports on a host system, helping in network security assessments.

## Features
- Fast and efficient scanning
- Supports both TCP and UDP protocols
- Customizable scan options

## Installation
To install the Custom Port Scanner, clone the repository and install the necessary dependencies:

```bash
git clone https://github.com/aniketrj45/Custom-Port-Scanner.git
cd Custom-Port-Scanner
# install dependencies
```

## Usage
To use the Port Scanner, run the following command:

```bash
python port_scanner.py [TARGET] [OPTIONS]
```

Replace `[TARGET]` with the target IP or hostname and adjust `[OPTIONS]` as needed.

## Architecture

```plaintext
          +-------------------+
          |    User Input     |
          +-------------------+
                    |
                    v
          +-------------------+
          |  Port Scanning    |
          +-------------------+
                    |
                    v
          +-------------------+
          |  Results Display   |
          +-------------------+
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for changes.

## License
This project is licensed under the MIT License.
