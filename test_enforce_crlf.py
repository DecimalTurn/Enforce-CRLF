import pytest
import subprocess
from unittest.mock import patch, mock_open
from enforce_crlf import needs_conversion_to_crlf, convert_lf_to_crlf, copy_file

def test_needs_conversion_to_crlf_no_conversion_needed():
    with patch("subprocess.check_output", return_value="text, with CRLF line terminators"):
        assert not needs_conversion_to_crlf("dummy.txt")

def test_needs_conversion_to_crlf_conversion_needed():
    with patch("subprocess.check_output", return_value="text, with LF line terminators"):
        assert needs_conversion_to_crlf("dummy.txt")

def test_convert_lf_to_crlf_success():
    with patch("subprocess.run") as mock_run:
        convert_lf_to_crlf("dummy.txt")
        mock_run.assert_called_once_with(["todos", "dummy.txt"], check=True)

def test_convert_lf_to_crlf_todos_not_found():
    with patch("subprocess.run", side_effect=FileNotFoundError):
        with pytest.raises(SystemExit):
            convert_lf_to_crlf("dummy.txt")

def test_convert_lf_to_crlf_error():
    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "todos")):
        with pytest.raises(SystemExit):
            convert_lf_to_crlf("dummy.txt")

def test_copy_file_success():
    with patch("os.makedirs") as mock_makedirs, patch("builtins.open", mock_open()) as mock_file:
        copy_file("source.txt", "destination.txt")
        mock_makedirs.assert_called_once()
        mock_file.assert_called()

def test_copy_file_error():
    with patch("builtins.open", side_effect=Exception("File error")), patch("builtins.print") as mock_print:
        copy_file("source.txt", "destination.txt")
        print(mock_print.call_args_list)  # Debug: Print all calls to mock_print