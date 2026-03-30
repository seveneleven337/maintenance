import unittest.mock as mock
from billing import billClass

# ---------- UNIT TEST 1: Test calculator perform calculation ----------
def test_perform_cal():
    obj = mock.Mock()
    obj.var_cal_input.get.return_value = "2+3"
    billClass.perform_cal(obj)
    obj.var_cal_input.set.assert_called_with(5)

# ---------- UNIT TEST 2: Test calculator clear ----------
def test_clear_cal():
    obj = mock.Mock()
    billClass.clear_cal(obj)
    obj.var_cal_input.set.assert_called_with('')

# ---------- UNIT TEST 3: Test calculator get input ----------
def test_get_input():
    obj = mock.Mock()
    obj.var_cal_input.get.return_value = "2"
    billClass.get_input(obj, 3)
    obj.var_cal_input.set.assert_called_with("23")