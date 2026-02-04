import json
import random

def create_mock_data():
    mock_data = {
        "data": []
    }

    # Generate 10 dummy ETF entries
    for i in range(1, 11):
        item = {
            "stock_code": f"0000{i}0",
            "stock_name": f"Test ETF {i}",
            "price": random.randint(10000, 20000),
            "net_asset": random.randint(50, 500), # Billion Won
            "fee": round(random.uniform(0.1, 0.5), 2),
            "returns": {
                "1D": round(random.uniform(-1, 1), 2),
                "1W": round(random.uniform(-2, 2), 2),
                "1M": round(random.uniform(-5, 5), 2),
                "3M": round(random.uniform(-10, 10), 2),
                "6M": round(random.uniform(-15, 15), 2),
                "1Y": round(random.uniform(-20, 20), 2),
            },
            "distributions": {
                f"{m}": random.randint(0, 100) for m in range(1, 13)
            }
        }
        # Add total distribution
        item["total_dist"] = sum(item["distributions"].values())
        mock_data["data"].append(item)

    with open("etf_data_mock.json", "w", encoding="utf-8") as f:
        json.dump(mock_data, f, ensure_ascii=False, indent=2)
    print("Created etf_data_mock.json")

if __name__ == "__main__":
    create_mock_data()
