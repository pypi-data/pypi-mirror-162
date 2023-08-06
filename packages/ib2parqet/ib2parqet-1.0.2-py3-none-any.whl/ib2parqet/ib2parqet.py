import csv

import xmltodict
from dateutil import parser


def load_ib_xml(path: str) -> dict:
    with open(path) as fh:
        return xmltodict.parse(fh.read())


def store_parqet_csv(path: str, data: list[dict]) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=data[0].keys(), delimiter=";")
        writer.writeheader()
        for x in data:
            writer.writerow(x)


def convert(data: dict) -> list[dict]:
    data = data["FlexQueryResponse"]["FlexStatements"]["FlexStatement"]["Trades"]["Trade"]
    data2 = data if type(data) is list else [data]
    data2 = [x for x in data2 if x["@assetCategory"] == "STK"]
    assert all(x["@currency"] == x["@ibCommissionCurrency"] for x in data2)
    return [
        {
            "broker": "Interactive Brokers",
            "currency": x["@currency"],
            "datetime": parser.parse(x["@dateTime"]).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "fee": abs(float(x["@ibCommission"])),
            "fxrate": abs(float(x["@fxRateToBase"])),
            "isin": x["@isin"],
            "price": abs(float(x["@tradePrice"])),
            "shares": abs(float(x["@quantity"])),
            "tax": abs(float(x["@taxes"])),
            "type": x["@buySell"],
        }
        for x in data2
    ]
