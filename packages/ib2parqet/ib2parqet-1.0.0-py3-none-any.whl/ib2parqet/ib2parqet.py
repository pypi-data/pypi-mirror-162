import csv

import xmltodict
from dateutil import parser


def load_ib_xml(path: str) -> dict:
    with open(path) as fh:
        return xmltodict.parse(fh.read())


def store_parqet_csv(path: str, data: list[dict]) -> None:
    with open(path, "w", newline="", encoding="cp1252") as fh:
        writer = csv.DictWriter(fh, fieldnames=data[0].keys(), delimiter=",")
        writer.writeheader()
        for x in data:
            writer.writerow(x)


def convert(data: dict, currency: str) -> list[dict]:
    data = data["FlexQueryResponse"]["FlexStatements"]["FlexStatement"]["Trades"]["Trade"]
    data2 = data if type(data) is list else [data]
    data2 = [x for x in data2 if x["@assetCategory"] == "STK"]
    assert all(x["@currency"] == x["@ibCommissionCurrency"] for x in data2)
    return [
        {
            "Securities Account": "Interactive Brokers",
            "Transaction Currency": currency,
            "Security Name": x["@description"],
            "Date": parser.parse(x["@dateTime"]).strftime("%Y-%m-%d"),
            "Time": parser.parse(x["@dateTime"]).strftime("%H:%M:%S"),
            "Fees": abs(float(x["@ibCommission"])) * abs(float(x["@fxRateToBase"])),
            "ISIN": x["@isin"],
            "Ticker Symbol": x["@symbol"],
            "Value": abs(float(x["@tradePrice"])) * abs(float(x["@quantity"])) * abs(float(x["@fxRateToBase"])),
            "Shares": abs(float(x["@quantity"])),
            "Taxes": abs(float(x["@taxes"])),
            "Type": x["@buySell"],
        }
        for x in data2
    ]
