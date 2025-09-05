# Accounting Dashboard

Simple web dashboard for uploading transaction CSVs and generating Profit & Loss, Balance Sheet, and GST summaries for a small mortgage broking business.

The dashboard now stores uploaded transactions and lets you filter results by financial year and BAS quarter. Summaries are displayed in tiles and the filtered raw transactions can be viewed in a table.

## Setup

```bash
pip install -r requirements.txt
```

## Running the app

```bash
python app.py
```

Open <http://localhost:5000> in your browser and upload a CSV with columns: `date, description, amount, category, gst`. After upload you can apply a financial year and BAS quarter filter to view summaries or inspect the raw data.

## Tests

```bash
pytest
```
