import os
import sys
import tkinter as tk
import unittest.mock as mock
from billing import billClass
from sales import salesClass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


def test_generate_and_search_bill(tmp_path, monkeypatch):
    root = tk.Tk()
    root.withdraw()

    bill_dir = tmp_path / "bill"
    bill_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr('sales.BILL_DIR', str(bill_dir))

    bill_obj = billClass.__new__(billClass)
    bill_obj.root = root
    bill_obj.var_cname = tk.StringVar(root, value="Alice")
    bill_obj.var_contact = tk.StringVar(root, value="999888777")
    bill_obj.cart_list = [['1', 'iPhone', '1000', '1', '10']]
    bill_obj.txt_bill_area = tk.Text(root)
    bill_obj.txt_bill_area.insert('1.0', "Alice\niPhone\n1000\n")
    bill_obj.invoice = "1001"
    bill_obj.chk_print = 0

    monkeypatch.setattr('billing.billClass.bill_top', lambda self: None)
    monkeypatch.setattr('billing.billClass.bill_middle', lambda self: None)
    monkeypatch.setattr('billing.billClass.bill_bottom', lambda self: None)
    monkeypatch.setattr('billing.messagebox.showinfo', lambda *args, **kwargs: None)

    billClass.generate_bill(bill_obj)

    bill_file = bill_dir / '1001.txt'
    assert bill_file.exists()
    content = bill_file.read_text()
    assert "Alice" in content
    assert "iPhone" in content
    assert "1000" in content

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