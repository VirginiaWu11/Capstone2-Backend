"""Generate CSVs of all coins from coins list endpoint from Coin Gecko.
"""

import csv
import requests

COINS_CSV_HEADERS = ["name", "symbol", "coin_gecko_id"]

COINS_FOR_SEED = requests.get("https://api.coingecko.com/api/v3/coins/list").json()

with open("generator/coins.csv", "w") as coins_csv:
    coins_writer = csv.DictWriter(coins_csv, fieldnames=COINS_CSV_HEADERS)
    coins_writer.writeheader()

    for coin in COINS_FOR_SEED:
        coins_writer.writerow(
            dict(name=coin["name"], symbol=coin["symbol"], coin_gecko_id=coin["id"])
        )
