# Accounting Dashboard

Simple web dashboard for uploading transaction CSVs and generating Profit & Loss, Balance Sheet, and GST summaries for a small mortgage broking business.

## Setup

```bash
pip install -r requirements.txt
```

## Running the app

```bash
python app.py
```

Open <http://localhost:5000> in your browser and upload a CSV with at least `date`, `description`, and `amount` columns. Optional `category` and `gst` columns can be provided. When missing, the app infers the category from the amount sign and estimates GST at 10%.

## Tests

```bash
pytest
```
