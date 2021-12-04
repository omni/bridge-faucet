OmniBridge faucet service
====

This service is monitoring transfers executed through the OmniBridge on the xDai chain and reward the tokens recipients with small amount of xdai.

## Run by docker CLI

1. Prepare `.env` file with the following (at least) variables definitons:

   ```bash
   FAUCET_PRIVKEY=cafe...cafe
   JSON_DB_DIR=/db
   INITIAL_START_BLOCK=123
   ```

   See below with the variables explanation.

2. Create the directory where the faucet service will store its data.

   ```bash
   mkdir ./db
   ```

3. Run the service 

   ```bash
   docker run -ti --rm -v $(pwd)/db:/db --env-file .env omnibridge/faucet:latest 
   ```
   
   _Note:_ the source mount point after the key `-v` is the directory created on the step 2. The destination mount point is the directory specified in the variable `JSON_DB_DIR`.

## Run by docker-compose

1. Create the directory where the faucet service will store its data.

   ```bash
   mkdir ./db
   ```

2. Initialize the `docker-compose.yml` file based on `docker-compose.yml.example`. Set proper values for the following variables (at least) there: `FAUCET_PRIVKEY`, `JSON_DB_DIR` and `INITIAL_START_BLOCK`.

   Make sure that the source mount point in the `volumes` section is the directory created on the step 1.

   See below with the variables explanation.

3. Run the service 

   ```bash
   docker-compose up -d
   ```

## Faucet configuration 

The following environment variables may be used to configure the faucet behavior:

1. `XDAI_RPC` - JSON RPC endpoint the faucet uses to monitor OB events and get data. **Default:** `https://xdai.poanetwork.dev`.
2. `BSC_OB` - an address of BSC-xDai OB mediator on the xDai side. **Default:** `0x59447362798334d3485c64D1e4870Fde2DDC0d75`.
3. `ETH_OB` - an address of ETH-xDai OB mediator on the xDai side. **Default:** `0xf6A78083ca3e2a662D6dd1703c939c8aCE2e268d`.
4. `MOONS_EXT` - an address of Rinkeby-xDai ERC20-to-ERC677 mediator for MOONs tokens on the xDai side. **Default:** `0x1E0507046130c31DEb20EC2f870ad070Ff266079`.
5. `BRICKS_EXT` - an address of Rinkeby-xDai ERC20-to-ERC677 mediator for BRICKs tokens on the xDai side. **Default:** `0xf85b17E64Bc788D0CB1A8c8C87c0d74e520c2A54`.
6. `FAUCET_PRIVKEY` - a private key of an account holding xdai to reward. **No default value!**.
7. `GAS_PRICE` - the gas price (in gwei) the faucet uses for reward transactions (pre-EIP1559 transactions). `-1` means to use EIP1559 transactions. **Default:** `-1`.
8. `HISTORICAL_BASE_FEE_DEPTH` - number of recent blocks to estimate the base fee as per gas (EIP1559 related). **Default:** `20`.
9. `MAX_PRIORITY_FEE` - the priority fee per gas (in gwei) used by the faucet (EIP1559 related). **Default:** `1`.
10. `MAX_FEE_RATIO` - a coefficient to adjust the base fee per gas acquired from the historical data (EIP1559 related). **Default:** `1.3`.
11. `FEE_LIMIT` - the higher bound of max fee per gas (in gwei) which is used in order to avoid expensive transactions (EIP1559 related). **Default:** `150`.
12. `GAS_LIMIT` - the gas limit the faucet uses for reward transactions. **Default:** `30000`.
13. `REWARD` - amount of xdai used as reward. **Default:** `0.005`.
14. `POLLING_INTERVAL` - amount of time (in seconds) between two subsequent cycles to discover OB transfers and send rewards. **Default:** `60`.
15. `INITIAL_START_BLOCK` - a block the first faucet's attempt to discover OB transfers starts from. **No default value!**.
16. `FINALIZATION_INTERVAL` - a number of blocks starting from the chain head to consider the chain as finalized. **Default:** `12`.
17. `JSON_DB_DIR` - a directory where the faucet service keeps its data. **No default value!**.
18. `JSON_START_BLOCK` - a name of JSON file where the last observed block is stored. **Default:** `faucet_start_block.json`.
19. `JSON_CONTRACTS` - a name of JSON file where addresses of recipient-contracts are stored. **Default:** `xdai-contracts.json`.
20. `TEST_TO_SEND` - make a transaction to itself just after running the service. **Default:** `false`.