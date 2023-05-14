#!/usr/bin/env python3

from dogecoinrpc.connection import DogecoinConnection
from pathlib import Path
from sys import maxsize
from xdg_base_dirs import xdg_config_home, xdg_config_dirs, xdg_data_home

import simplejson
import click

@click.command()
@click.option("--startat", default=None, help="Height of the block to start" ,type=int)
@click.option("--numblocks", default=100, help="Number of blocks to analyze", type=int)
@click.option("--blockmaxbytes", default=768000, help="Maximum size of a block in bytes", type=int)
@click.option("--user", default=None, help="Name of the RPC user", type=str)
def main(startat, numblocks, blockmaxbytes, user) -> None:
    config_file = Path(xdg_data_home()) / "dogeutils" / "auth.json"
    with open(config_file, 'r') as f:
        config = simplejson.load(f)

    if user is None:
        print("No user provided; exiting")
        exit(1)
    else:
        client = DogecoinConnection(user, config[user], 'localhost', 22555)

    if startat is None:
        startat = client.getblockcount()

    # make the percentages obvious
    blockmaxbytes /= 100

    res = {
        "startingHeight": startat,
        "minTxCount": maxsize,
        "maxTxCount": 0,
        "totalTxCount": 0,
        "minBlockSize": maxsize,
        "maxBlockSize": 0,
        "minBlockFill": 0,
        "minFillPercent": maxsize,
        "maxFillPercent": 0,
        "totalBlockSize": 0,
    }

    hash = client.getblockhash(startat)

    for i in range(1, numblocks):
        block = client.getblock(hash)
        block_size = block["size"]

        res["minBlockSize"] = min(block_size, res["minBlockSize"])
        res["maxBlockSize"] = max(block_size, res["maxBlockSize"])
        res["totalBlockSize"] += block_size

        block_tx_count = len(block["tx"])

        res["minTxCount"] = min(block_tx_count, res["minTxCount"])
        res["maxTxCount"] = max(block_tx_count, res["maxTxCount"])
        res["totalTxCount"] += block_tx_count

        block_fill_percent = block_size / blockmaxbytes

        res["minFillPercent"] = min(block_fill_percent, res["minFillPercent"])
        res["maxFillPercent"] = max(block_fill_percent, res["maxFillPercent"])

        hash = block["previousblockhash"]

    res["averageSize"] = res["totalBlockSize"] / numblocks
    res["averageTxCount"] = res["totalTxCount"] / numblocks
    res["averageFillPercent"] = res["totalBlockSize"] / (numblocks * blockmaxbytes)

    print(simplejson.dumps(res, indent=2))

if __name__ == '__main__':
    main()
