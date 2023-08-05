# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['starknet_devnet', 'starknet_devnet.blueprints']

package_data = \
{'': ['*'],
 'starknet_devnet': ['accounts_artifacts/OpenZeppelin/0.2.1/Account.cairo/*']}

install_requires = \
['Flask[async]>=2.0.3,<2.1.0',
 'Werkzeug>=2.0.3,<2.1.0',
 'cairo-lang==0.9.1',
 'cloudpickle>=2.1.0,<2.2.0',
 'crypto-cpp-py>=1.0.4,<1.1.0',
 'flask-cors>=3.0.10,<3.1.0',
 'marshmallow>=3.17.0,<3.18.0',
 'meinheld>=1.0.2,<1.1.0',
 'typing-extensions>=4.3.0,<4.4.0']

entry_points = \
{'console_scripts': ['starknet-devnet = starknet_devnet.server:main']}

setup_kwargs = {
    'name': 'starknet-devnet',
    'version': '0.2.8',
    'description': 'A local testnet for Starknet',
    'long_description': '## Introduction\n\nA Flask wrapper of Starknet state. Similar in purpose to Ganache.\n\nAims to mimic Starknet\'s Alpha testnet, but with simplified functionality.\n\n## Contents\n\n- [Install](#install)\n- [Disclaimer](#disclaimer)\n- [Run](#run)\n- [Interaction](#interaction)\n- [JSON-RPC API](#json-rpc-api)\n- [Dumping and Loading](#dumping)\n- [Hardhat Integration](#hardhat-integration)\n- [L1-L2 Postman Communication](#postman-integration)\n- [Block Explorer](#block-explorer)\n- [Lite Mode](#lite-mode)\n- [Restart](#restart)\n- [Advancing time](#advancing-time)\n- [Contract debugging](#contract-debugging)\n- [Predeployed accounts](#predeployed-accounts)\n- [Mint token - Local faucet](#mint-token---local-faucet)\n- [Devnet speed-up troubleshooting](#devnet-speed-up-troubleshooting)\n- [Development](#development)\n\n## Install\n\n```text\npip install starknet-devnet\n```\n\n### Requirements\n\nWorks with Python versions >=3.7.2 and <3.10.\n\nOn Ubuntu/Debian, first run:\n\n```text\nsudo apt install -y libgmp3-dev\n```\n\nOn Mac, you can use `brew`:\n\n```text\nbrew install gmp\n```\n\n## Disclaimer\n\n- Devnet should not be used as a replacement for Alpha testnet. After testing on Devnet, be sure to test on testnet (alpha-goerli)!\n- Specifying a block by its hash/number is not supported for contract calls. All interaction is done with the latest block.\n- There is no pending block. A new block is generated with each transaction.\n- Sending transactions with max_fee set to 0 is supported (not supported on alpha-mainnet or alpha-goerli).\n\n## Run\n\nInstalling the package adds the `starknet-devnet` command.\n\n```text\nusage: starknet-devnet [-h] [-v] [--host HOST] [--port PORT]\n\nRun a local instance of Starknet Devnet\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -v, --version         Print the version\n  --host HOST           Specify the address to listen at; defaults to\n                        127.0.0.1 (use the address the program outputs on\n                        start)\n  --port PORT, -p PORT  Specify the port to listen at; defaults to 5050\n  --load-path LOAD_PATH\n                        Specify the path from which the state is loaded on\n                        startup\n  --dump-path DUMP_PATH\n                        Specify the path to dump to\n  --dump-on DUMP_ON     Specify when to dump; can dump on: exit, transaction\n  --lite-mode           Applies all lite-mode-* optimizations by disabling some features.\n  --lite-mode-block-hash\n                        Disables block hash calculation\n  --lite-mode-deploy-hash\n                        Disables deploy tx hash calculation\n  --accounts ACCOUNTS   Specify the number of accounts to be predeployed;\n                        defaults to 10\n  --initial-balance INITIAL_BALANCE, -e INITIAL_BALANCE\n                        Specify the initial balance of accounts to be\n                        predeployed; defaults to 1e+21 (wei)\n  --seed SEED           Specify the seed for randomness of accounts to be\n                        predeployed\n  --start-time START_TIME\n                        Specify the start time of the genesis block in Unix\n                        time seconds\n  --gas-price GAS_PRICE, -g GAS_PRICE\n                        Specify the gas price in wei per gas unit; defaults to\n                        1e+11\n```\n\nYou can run `starknet-devnet` in a separate shell, or you can run it in background with `starknet-devnet &`.\nCheck that it\'s alive by running the following (address and port my vary if you specified a different one with `--host` or `--port`):\n\n```\ncurl http://127.0.0.1:5050/is_alive\n```\n\n### Run with Docker\n\nDevnet is available as a Docker image ([shardlabs/starknet-devnet](https://hub.docker.com/repository/docker/shardlabs/starknet-devnet)):\n\n```text\ndocker pull shardlabs/starknet-devnet:<TAG>\n```\n\n#### Versions and Tags\n\nImage tags correspond to Devnet versions as on PyPI and GitHub, with the `latest` tag used for the latest image. These images are built for linux/amd64. To use the arm64 versions, since `0.1.23` you can append `-arm` to the tag. E.g.:\n\n- `shardlabs/starknet-devnet:0.2.8` - image for the amd64 architecture\n- `shardlabs/starknet-devnet:0.2.8-arm` - image for the arm64 architecture\n- `shardlabs/starknet-devnet:latest-arm`\n\nBy appending the `-seed0` suffix, you can access images which [predeploy funded accounts](#predeployed-accounts) with `--seed 0`, thus always deploying the same set of accounts. E.g.:\n\n- `shardlabs/starknet-devnet:0.2.8-seed0`\n- `shardlabs/starknet-devnet:latest-seed0`\n- `shardlabs/starknet-devnet:0.2.8-arm-seed0`\n\nThe server inside the container listens to the port 5050, which you need to publish to a desired `<PORT>` on your host machine:\n\n```text\ndocker run -p [HOST:]<PORT>:5050 shardlabs/starknet-devnet\n```\n\nE.g. if you want to use your host machine\'s `127.0.0.1:5050`, you need to run:\n\n```text\ndocker run -p 127.0.0.1:5050:5050 shardlabs/starknet-devnet\n```\n\nYou may ignore any address-related output logged on container startup (e.g. `Running on all addresses` or `Running on http://172.17.0.2:5050`). What you will use is what you specified with the `-p` argument.\n\nIf you don\'t specify the `HOST` part, the server will indeed be available on all of your host machine\'s addresses (localhost, local network IP, etc.), which may present a security issue if you don\'t want anyone from the local network to access your Devnet instance.\n\n## Interaction\n\n- Interact with Devnet as you would with the official Starknet [Alpha testnet](https://www.cairo-lang.org/docs/hello_starknet/amm.html?highlight=alpha#interaction-examples).\n- The exact underlying API is not exposed for the same reason Alpha testnet does not expose it.\n- To use Devnet with Starknet CLI, provide Devnet\'s URL to the `--gateway_url` and `--feeder_gateway_url` options of Starknet CLI commands.\n- The following Starknet CLI commands are supported:\n  - `call`\n  - `declare`\n  - `deploy`\n  - `estimate_fee`\n  - `get_block` (currently pending block is not supported)\n  - `get_block_traces`\n  - `get_class_by_hash`\n  - `get_class_hash_at`\n  - `get_code`\n  - `get_full_contract`\n  - `get_state_update`\n  - `get_storage_at`\n  - `get_transaction`\n  - `get_transaction_receipt`\n  - `get_transaction_trace`\n  - `invoke`\n  - `tx_status`\n- The following Starknet CLI commands are **not** supported:\n  - `get_contract_addresses`\n\n## JSON-RPC API\n\nDevnet also partially supports JSON-RPC API (v0.15.0: [specifications](https://github.com/starkware-libs/starknet-specs/blob/606c21e06be92ea1543fd0134b7f98df622c2fbf/api/starknet_api_openrpc.json)) and WRITE API (v0.3.0: [specifications](https://github.com/starkware-libs/starknet-specs/blob/4c31d6f9f842028ca8cfd073ec8d0d5089b087c4/api/starknet_write_api.json)). It can be reached under `/rpc`. For an example:\n\n```\nPOST /rpc\n{\n  "jsonrpc": "2.0",\n  "method": "starknet_protocolVersion",\n  "params": [],\n  "id": 0\n}\n```\n\nResponse:\n\n```\n{\n  "id": 0,\n  "jsonrpc": "2.0",\n  "result": "0x302e382e30"\n}\n```\n\n## Hardhat integration\n\nIf you\'re using [the Hardhat plugin](https://github.com/Shard-Labs/starknet-hardhat-plugin), see [here](https://github.com/Shard-Labs/starknet-hardhat-plugin#runtime-network) on how to edit its config file to integrate Devnet.\n\n## Postman integration\n\nPostman is a Starknet utility that allows testing L1 <> L2 interaction. To utilize this, you can use [`starknet-hardhat-plugin`](https://github.com/Shard-Labs/starknet-hardhat-plugin), as witnessed in [this example](https://github.com/Shard-Labs/starknet-hardhat-example/blob/master/test/postman.test.ts). Or you can directly interact with the two Postman-specific endpoints:\n\n### Postman - Load\n\n```\nPOST /postman/load_l1_messaging_contract\n{\n  "networkUrl": "http://localhost:8545",\n  "address": "0x123...def"\n}\n```\n\nLoads a `StarknetMockMessaging` contract. The `address` parameter is optional; if provided, the `StarknetMockMessaging` contract will be fetched from that address, otherwise a new one will be deployed.\n\n`networkUrl` is the URL of the JSON-RPC API of the L1 node you\'ve run locally or that already exists; possibilities include, and are not limited to:\n\n- [Goerli testnet](https://goerli.net/)\n- [Ganache](https://www.npmjs.com/package/ganache)\n- [Geth](https://github.com/ethereum/go-ethereum#docker-quick-start)\n- [Hardhat node](https://hardhat.org/hardhat-network/#running-stand-alone-in-order-to-support-wallets-and-other-software).\n\n### Postman - Flush\n\n```\nPOST /postman/flush\n```\n\nGoes through the newly enqueued messages, sending them from L1 to L2 and from L2 to L1. Requires no body.\n\n### Postman - disclaimer\n\nThis method of L1 <> L2 communication testing differs from Starknet Alpha networks. Taking the [L1L2Example.sol](https://www.cairo-lang.org/docs/_static/L1L2Example.sol) contract in the [starknet documentation](https://www.cairo-lang.org/docs/hello_starknet/l1l2.html):\n\n```\nconstructor(IStarknetCore starknetCore_) public {\n    starknetCore = starknetCore_;\n}\n```\n\nThe constructor takes an `IStarknetCore` contract as argument, however for Devnet L1 <> L2 communication testing, this will have to be replaced with the [MockStarknetMessaging.sol](https://github.com/starkware-libs/cairo-lang/blob/master/src/starkware/starknet/testing/MockStarknetMessaging.sol) contract:\n\n```\nconstructor(MockStarknetMessaging mockStarknetMessaging_) public {\n    starknetCore = mockStarknetMessaging_;\n}\n```\n\n## Dumping\n\nTo preserve your Devnet instance for future use, there are several options:\n\n- Dumping on exit (handles Ctrl+C, i.e. SIGINT, doesn\'t handle SIGKILL):\n\n```\nstarknet-devnet --dump-on exit --dump-path <PATH>\n```\n\n- Dumping after each transaction (done in background, doesn\'t block):\n\n```\nstarknet-devnet --dump-on transaction --dump-path <PATH>\n```\n\n- Dumping on request (replace `<HOST>`, `<PORT>` and `<PATH>` with your own):\n\n```\ncurl -X POST http://<HOST>:<PORT>/dump -d \'{ "path": <PATH> }\' -H "Content-Type: application/json"\n```\n\n### Loading\n\nTo load a preserved Devnet instance, the options are:\n\n- Loading on startup:\n\n```\nstarknet-devnet --load-path <PATH>\n```\n\n- Loading on request:\n\n```\ncurl -X POST http://<HOST>:<PORT>/load -d \'{ "path": <PATH> }\' -H "Content-Type: application/json"\n```\n\n### Enabling dumping and loading with Docker\n\nTo enable dumping and loading if running Devnet in a Docker container, you must bind the container path with the path on your host machine.\n\nThis example:\n\n- Relies on [Docker bind mount](https://docs.docker.com/storage/bind-mounts/); try [Docker volume](https://docs.docker.com/storage/volumes/) instead.\n- Assumes that `/actual/dumpdir` exists. If unsure, use absolute paths.\n- Assumes you are listening on `127.0.0.1:5050`.\n\nIf there is `dump.pkl` inside `/actual/dumpdir`, you can load it with:\n\n```\ndocker run \\\n  -p 127.0.0.1:5050:5050 \\\n  --mount type=bind,source=/actual/dumpdir,target=/dumpdir \\\n  shardlabs/starknet-devnet \\\n  --load-path /dumpdir/dump.pkl\n```\n\nTo dump to `/actual/dumpdir/dump.pkl` on Devnet shutdown, run:\n\n```\ndocker run \\\n  -p 127.0.0.1:5050:5050 \\\n  --mount type=bind,source=/actual/dumpdir,target=/dumpdir \\\n  shardlabs/starknet-devnet \\\n  --dump-on exit --dump-path /dumpdir/dump.pkl\n```\n\n## Block explorer\n\nA local block explorer (Voyager), as noted [here](https://voyager.online/local-version/), apparently cannot be set up to work with Devnet. Read more in [this issue](https://github.com/Shard-Labs/starknet-devnet/issues/60).\n\n## Block\n\nDevnet start with a genesis block.\n\nGENESIS_BLOCK_NUMBER = 0\n\nGENESIS_BLOCK_HASH = "0x0"\n\nYou can create empty block without transaction.\n\n```\nPOST /create_block\n```\n\nResponse:\n\n```\n{\n    "transactions": [],\n    "parent_block_hash": "0x0",\n    "timestamp": 1659457385,\n    "state_root": "004bee3ee...",\n    "gas_price": "0x174876e800",\n    "sequencer_address": "0x4bbfb0d1aa...",\n    "transaction_receipts": [],\n    "starknet_version": "0.9.1",\n    "block_hash": "0x1",\n    "block_number": 1,\n    "status": "ACCEPTED_ON_L2"\n}\n```\n\n## Lite mode\n\nTo improve Devnet performance, instead of calculating the actual hash of deployment transactions and blocks, sequential numbering can be used (0x0, 0x1, 0x2, ...).\n\nConsider passing these CLI flags on Devnet startup:\n\n- `--lite-mode` enables all of the optimizations described below (same as using all of the flags below)\n- `--lite-mode-deploy-hash`\n  - disables the calculation of transaction hash for deploy transactions\n- `--lite-mode-block-hash`\n  - disables the calculation of block hash\n  - disables get_state_update functionality\n\n## Restart\n\nDevnet can be restarted by making a `POST /restart` request. All of the deployed contracts, blocks and storage updates will be restarted to the empty state. If you\'re using [the Hardhat plugin](https://github.com/Shard-Labs/starknet-hardhat-plugin#restart), run `await starknet.devnet.restart()`.\n\n## Advancing time\n\nBlock timestamp can be manipulated by seting the exact time or seting the time offset. Timestamps methods won\'t generate a new block, but they will modify the time of the following blocks. All values should be set in [Unix time](https://en.wikipedia.org/wiki/Unix_time) and seconds.\n\n### Set time\n\nSets the exact time of the next generated block. All subsequent blocks will keep the set offset.\n\n```\nPOST /set_time\n{\n    "time": TIME_IN_SECONDS\n}\n```\n\nWarning: block time can be set in the past and lead to unexpected behaviour!\n\n### Increase time\n\nIncreases the time offset for each generated block.\n\n```\nPOST /increase_time\n{\n    "time": TIME_IN_SECONDS\n}\n```\n\n### Start time arg\n\nDevnet can be started with the `--start-time` argument.\n\n```\nstarknet-devnet --start-time START_TIME_IN_SECONDS\n```\n\n## Contract debugging\n\nIf your contract is using `print` in cairo hints (it was compiled with the `--disable-hint-validation` flag), Devnet will output those lines together with its regular server output. Read more about hints [here](https://www.cairo-lang.org/docs/how_cairo_works/hints.html). To filter out just your debug lines, redirect stderr to /dev/null when starting Devnet:\n\n```\nstarknet-devnet 2> /dev/null\n```\n\nTo enable printing with a dockerized version of Devnet set `PYTHONUNBUFFERED=1`:\n\n```\ndocker run -p 127.0.0.1:5050:5050 -e PYTHONUNBUFFERED=1 shardlabs/starknet-devnet\n```\n\n## Predeployed accounts\n\nDevnet predeploys `--accounts` with some `--initial-balance`. The accounts get charged for transactions according to the `--gas-price`. A `--seed` can be used to regenerate the same set of accounts. Read more about it in the [Run section](#run).\n\nTo get the code of the account (currently OpenZeppelin v0.2.1), use one of the following:\n\n- `GET /get_code?contractAddress=<ACCOUNT_ADDRESS>`\n- [Starknet CLI](https://www.cairo-lang.org/docs/hello_starknet/cli.html#get-code): `starknet get_code --contract_address <ACCOUNT_ADDRESS> --feeder_gateway_url <DEVNET_URL>`\n- [OpenZeppelin\'s cairo-contract repository](https://github.com/OpenZeppelin/cairo-contracts/tree/v0.2.1)\n\nYou can use the accounts in e.g. [starknet-hardhat-plugin](https://github.com/Shard-Labs/starknet-hardhat-plugin) via:\n\n```typescript\nconst account = await starknet.getAccountFromAddress(\n  ADDRESS,\n  PRIVATE_KEY,\n  "OpenZeppelin"\n);\n```\n\n### Fetch predeployed accounts\n\n```\nGET /predeployed_accounts\n```\n\nResponse:\n\n```\n[\n  {\n    "initial_balance": 1e+21,\n    "address": "0x7c3e2...",\n    "private_key": "0x6160...",\n    "public_key": "0x6a5540..."\n  },\n  ...\n]\n```\n\n### Fetch account balance\n\n```\nGET /account_balance?address=<HEX_ADDRESS>\n```\n\nResponse:\n\n```\n{\n  "amount": 123...456,\n  "unit": "wei"\n}\n```\n\n## Mint token - Local faucet\n\nOther than using prefunded predeployed accounts, you can also add funds to an account that you deployed yourself.\n\nThe ERC20 contract used for minting ETH tokens and charging fees is at: `0x62230ea046a9a5fbc261ac77d03c8d41e5d442db2284587570ab46455fd2488`\n\n### Query fee token address\n\n```\nGET /fee_token\n```\n\nResponse:\n\n```\n{\n  "symbol":"ETH",\n  "address":"0x62230ea046a9a5fbc261ac77d03c8d41e5d442db2284587570ab46455fd2488",\n}\n```\n\n### Mint with a transaction\n\nBy not setting the `lite` parameter or by setting it to `false`, new tokens will be minted in a separate transaction. You will receive the hash of this transaction, as well as the new balance after minting in the response.\n\n`amount` needs to be an integer (or a float whose fractional part is 0, e.g. `1000.0` or `1e21`)\n\n```\nPOST /mint\n{\n    "address": "0x6e3205f...",\n    "amount": 500000\n}\n```\n\nResponse:\n\n```\n{\n    "new_balance": 500000,\n    "unit": "wei",\n    "tx_hash": "0xa24f23..."\n}\n```\n\n### Mint lite\n\nBy setting the `lite` parameter, new tokens will be minted without generating a transaction, thus executing faster.\n\n```\nPOST /mint\n{\n    "address": "0x6e3205f...",\n    "amount": 500000,\n    "lite": true\n}\n```\n\nResponse:\n\n```\n{\n    "new_balance": 500000,\n    "unit": "wei",\n    "tx_hash": null\n}\n```\n\n## Devnet speed-up troubleshooting\n\nIf you are not satisfied with Devnet\'s performance, consider the following:\n\n- Make sure you are using the latest version of Devnet because new improvements are added regularly.\n- Try using [lite-mode](#lite-mode).\n- If minting tokens, set the [lite parameter](#mint-lite).\n- Using an [installed Devnet](#install) should be faster than [running it with Docker](#run-with-docker).\n- If you are [running Devnet with Docker](#run-with-docker) on an ARM machine (e.g. M1), make sure you are using [the appropriate image tag](#versions-and-tags)\n- If Devnet has been running for some time, try restarting it (either by killing it or by using the [restart functionality](#restart)).\n- Keep in mind that:\n  - The first transaction is always a bit slower due to lazy loading.\n  - Tools you use for testing (e.g. [the Hardhat plugin](https://github.com/Shard-Labs/starknet-hardhat-plugin)) add their own overhead.\n  - Bigger contracts are more time consuming.\n\n## Development\n\nIf you\'re a developer willing to contribute, be sure to have installed [Poetry](https://pypi.org/project/poetry/) and all the dependency packages by running the following script. You are expected to have npm.\n\n```text\n./scripts/install_dev_tools.sh\n```\n\n### Development - Run\n\n```text\npoetry run starknet-devnet\n```\n\n### Development - Run in debug mode\n\n```text\n./scripts/starknet_devnet_debug.sh\n```\n\n### Development - Lint\n\n```text\n./scripts/lint.sh\n```\n\n### Development - Test in parallel\n```bash\n./scripts/test.sh \n#optional you can pass <TEST_DIR>/\n```\nor manually you can set -s -v for verbose and replace \'auto\' with number of workers (recommended same as CPU cores)\n```bash\npoetry run pytest -n auto --dist loadscope test/  \n# parallel testing using auto detect number of CPU cores and spawn same amount of workers\n```\n\n### Development - Test\n\nWhen running tests locally, do it from the project root:\n\n```bash\n./scripts/compile_contracts.sh # first generate the artifacts\n\npoetry run pytest test/\n\npoetry run pytest -s -v test/ # for more verbose output\n\npoetry run pytest test/<TEST_FILE> # for a single file\n\npoetry run pytest test/<TEST_FILE>::<TEST_CASE> # for a single test case\n```\n\n### Development - Check versioning consistency\n\n```\n./scripts/check_versions.sh\n```\n\n### Development - working with a local version of cairo-lang:\n\nIn `pyproject.toml` under `[tool.poetry.dependencies]` specify\n\n```\ncairo-lang = { path = "your-cairo-lang-package.zip" }\n```\n\n### Development - Build\n\nYou don\'t need to build anything to be able to run locally, but if you need the `*.whl` or `*.tar.gz` artifacts, run\n\n```text\npoetry build\n```\n',
    'author': 'FabijanC',
    'author_email': 'fabijan.corak@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Shard-Labs/starknet-devnet',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.2,<3.10',
}


setup(**setup_kwargs)
