import os
import sys
import tkinter as tk
import unittest.mock as mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sales import salesClass
from billing import billClass

# ---------- INTEGRATION TEST 1: Test sales search with valid invoice ----------
def test_sales_search_valid(tmp_path, monkeypatch):
    root = tk.Tk()
    root.withdraw()

    bill_dir = tmp_path / "bill"
    bill_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr('sales.BILL_DIR', str(bill_dir))

    # Build billing object minimal state for generate_bill
    bill_obj = billClass.__new__(billClass)
    bill_obj.root = root
    bill_obj.var_cname = tk.StringVar(root, value="Alice")
    bill_obj.var_contact = tk.StringVar(root, value="999888777")
    bill_obj.cart_list = [['1', 'iPhone', '1000', '1', '10']]
    bill_obj.txt_bill_area = mock.Mock()
    bill_obj.txt_bill_area.get.return_value = "Alice\niPhone\n1000\n"
    bill_obj.invoice = "1001"
    bill_obj.chk_print = 0

    monkeypatch.setattr('billing.billClass.bill_top', lambda self: None)
    monkeypatch.setattr('billing.billClass.bill_middle', lambda self: None)
    monkeypatch.setattr('billing.billClass.bill_bottom', lambda self: None)
    monkeypatch.setattr('billing.messagebox.showinfo', lambda *args, **kwargs: None)

    billClass.generate_bill(bill_obj)

    assert (bill_dir / '1001.txt').exists()

    # Create sales object and run search
    sales_obj = salesClass.__new__(salesClass)
    sales_obj.root = root
    sales_obj.var_invoice = tk.StringVar(root, value="1001")
    sales_obj.blll_list = ['1001']
    sales_obj.bill_area = tk.Text(root)

    salesClass.search(sales_obj)

    displayed_text = sales_obj.bill_area.get('1.0', 'end-1c')
    assert 'Alice' in displayed_text
    assert 'iPhone' in displayed_text
    assert '1000' in displayed_text

    sales_obj.bill_area.delete('1.0', 'end')
    assert sales_obj.bill_area.get('1.0', 'end-1c') == ''

    root.destroy()


# ---------- INTEGRATION TEST 2: Test sales search with invalid invoice ----------
def test_sales_search_invalid(tmp_path, monkeypatch):
    root = tk.Tk()
    root.withdraw()

    bill_dir = tmp_path / "bill"
    bill_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr('sales.BILL_DIR', str(bill_dir))

    # build one valid bill so the invalid search path works
    bill_obj = billClass.__new__(billClass)
    bill_obj.root = root
    bill_obj.var_cname = tk.StringVar(root, value="Alice")
    bill_obj.var_contact = tk.StringVar(root, value="999888777")
    bill_obj.cart_list = [['1', 'iPhone', '1000', '1', '10']]
    bill_obj.txt_bill_area = mock.Mock()
    bill_obj.txt_bill_area.get.return_value = "Alice\niPhone\n1000\n"
    bill_obj.invoice = "1001"
    bill_obj.chk_print = 0

    monkeypatch.setattr('billing.billClass.bill_top', lambda self: None)
    monkeypatch.setattr('billing.billClass.bill_middle', lambda self: None)
    monkeypatch.setattr('billing.billClass.bill_bottom', lambda self: None)
    monkeypatch.setattr('billing.messagebox.showinfo', lambda *args, **kwargs: None)

    billClass.generate_bill(bill_obj)

    assert (bill_dir / '1001.txt').exists()

    # Perform invalid search with invoice not in list
    sales_obj = salesClass.__new__(salesClass)
    sales_obj.root = root
    sales_obj.var_invoice = tk.StringVar(root, value="999")
    sales_obj.blll_list = ['1001']
    sales_obj.bill_area = tk.Text(root)

    with mock.patch('sales.messagebox.showerror') as mock_error:
        salesClass.search(sales_obj)

    mock_error.assert_called_with("Error", "Invalid Invoice No.", parent=root)

    root.destroy()