import io
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import parse_transactions


def test_parse_transactions():
    data = """date,description,amount,category,gst
2024-01-01,Fee,100,income,10
2024-01-02,Rent,50,expense,5
2024-01-03,Furniture,200,asset,20
2024-01-04,Loan,100,liability,0
"""
    summary = parse_transactions(io.StringIO(data))
    assert summary['income'] == 100
    assert summary['expenses'] == 50
    assert summary['profit_loss'] == 50
    assert summary['assets'] == 200
    assert summary['liabilities'] == 100
    assert summary['gst_collected'] == 10
    assert summary['gst_paid'] == 5
    assert summary['gst_net'] == 5


def test_parse_transactions_infer_columns():
    data = """Date,Description,Amount
2024-01-01,Sale,100
2024-01-02,Rent,-50
"""
    summary = parse_transactions(io.StringIO(data))
    assert summary['income'] == 100
    assert summary['expenses'] == 50
    assert summary['profit_loss'] == 50
    # GST inferred at 10%
    assert summary['gst_collected'] == 10
    assert summary['gst_paid'] == 5
    assert summary['gst_net'] == 5
