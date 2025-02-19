import requests
import yaml

def ingest_data():
    with open("app/data/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    # Dummy data for demonstration – replace with actual ingestion logic.
    data = {"sample": "data", "source": config.get("data_source", "N/A")}
    return data

if __name__ == "__main__":
    data = ingest_data()
    print("Data ingested:", data)
