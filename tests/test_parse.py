import io
import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import parse_transactions, load_transactions, compute_summary


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


def test_parse_transactions_case_insensitive_and_no_gst():
    data = """Date,Description,Amount,Category
2024-01-01,Fee,100,INCOME
2024-01-02,Rent,50,Expense
"""
    summary = parse_transactions(io.StringIO(data))
    assert summary['income'] == 100
    assert summary['expenses'] == 50
    assert summary['gst_collected'] == 0
    assert summary['gst_paid'] == 0
    assert summary['gst_net'] == 0


def test_compute_summary_with_date_filter():
    data = """date,description,amount,category,gst
2024-07-01,Sale,100,income,10
2024-08-01,Rent,50,expense,5
2025-01-15,Sale2,200,income,20
"""
    df = load_transactions(io.StringIO(data))
    summary_full = compute_summary(df)
    summary_q1 = compute_summary(df, start_date=pd.Timestamp(2024, 7, 1), end_date=pd.Timestamp(2024, 9, 30))
    assert summary_full['income'] == 300
    assert summary_q1['income'] == 100
