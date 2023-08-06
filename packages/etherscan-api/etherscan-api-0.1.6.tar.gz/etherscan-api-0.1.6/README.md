# etherscan-api module


EtherScan.io API python bindings

## Description

This module is written as an effort to provide python bindings to the EtherScan.io API, which can be found at:
https://etherscan.io/apis. If you are interacting with a contract on the Ropsten Testnet please use
https://ropsten.etherscan.io/apis.
In order to use this, you must attain an Etherscan user account, and generate an API key.

In order to use the API, you must provide an API key at runtime, which can be found at the Etherscan.io API website.
If you'd like to use the provided examples without altering them, then the JSON file `api_key.json` must be stored in
the base directory. Its format is as follows:

    { "key" : "YourApiKeyToken" }

with `YourApiKeyToken` is your provided API key token from EtherScan.io

## Installation

To install the package to your computer, simply run the following command in the base directory:

    python3 -m pip install py-etherscan-api

## Available bindings

Currently, only the following Etherscan.io API modules are available:

- accounts
- contracts
- stats
- tokens
- proxies
- blocks
- transactions
- Logs
- Gas Tracker

The remaining available modules provided by Etherscan.io will be added eventually...

## Available Networks

Currently, this works for the following networks:

- Mainnet
- Ropsten

