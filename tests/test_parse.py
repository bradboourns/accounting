import io
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import (
    parse_transactions,
    load_transactions,
    filter_transactions,
    calculate_summary,
)


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


def test_filter_transactions_financial_year_and_bas():
    data = """date,description,amount,category,gst
2023-08-01,Job1,100,income,10
2023-11-05,Rent1,50,expense,5
2024-02-10,Job2,200,income,20
2024-03-12,Rent2,80,expense,8
2024-05-20,Job3,150,income,15
"""
    df = load_transactions(io.StringIO(data))
    filtered = filter_transactions(df, financial_year=2024, bas_period='Q3')
    summary = calculate_summary(filtered)
    assert summary['income'] == 200
    assert summary['expenses'] == 80
    assert summary['gst_collected'] == 20
    assert summary['gst_paid'] == 8
