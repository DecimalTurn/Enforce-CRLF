import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from enforce_crlf import (
    analyze_line_endings,
    analyze_line_endings_data,
    get_line_endings_issue,
    convert_to_crlf,
    copy_file,
)


def test_analyze_line_endings_crlf_only():
    with patch("builtins.open", mock_open(read_data=b"a\r\nb\r\nc")):
        counts, label = analyze_line_endings("dummy.txt")
        assert counts == {"LF": 0, "CRLF": 2, "CR": 0}
        assert label == "CRLF"


def test_analyze_line_endings_mixed_lf_crlf():
    with patch("builtins.open", mock_open(read_data=b"a\nb\r\nc")):
        counts, label = analyze_line_endings("dummy.txt")
        assert counts == {"LF": 1, "CRLF": 1, "CR": 0}
        assert label == "Mixed (LF + CRLF)"


def test_analyze_line_endings_mixed_all_three():
    with patch("builtins.open", mock_open(read_data=b"a\nb\r\nc\rd")):
        counts, label = analyze_line_endings("dummy.txt")
        assert counts == {"LF": 1, "CRLF": 1, "CR": 1}
        assert label == "Mixed (LF + CRLF + CR)"


def test_analyze_line_endings_no_terminators():
    with patch("builtins.open", mock_open(read_data=b"abc")):
        counts, label = analyze_line_endings("dummy.txt")
        assert counts == {"LF": 0, "CRLF": 0, "CR": 0}
        assert label is None


def test_get_line_endings_issue_lone_cr():
    with patch("builtins.open", mock_open(read_data=b"a\rb\r\nc")):
        assert get_line_endings_issue("dummy.txt") == "contains lone CR line endings"


def test_get_line_endings_issue_lf():
    with patch("builtins.open", mock_open(read_data=b"a\nb\nc")):
        assert get_line_endings_issue("dummy.txt") == "needs LF to CRLF conversion"


def test_get_line_endings_issue_mixed_label():
    with patch("builtins.open", mock_open(read_data=b"a\nb\r\nc")):
        assert get_line_endings_issue("dummy.txt") == "contains mixed line endings: Mixed (LF + CRLF)"


def test_convert_lf_to_crlf_success():
    data = b"a\nb\nc"
    counts, _ = analyze_line_endings_data(data)
    with patch("builtins.open", mock_open(read_data=b"a\nb\nc")) as mocked_open:
        convert_to_crlf("dummy.txt", issue_reason="needs LF to CRLF conversion", data=data, counts=counts)
        mocked_open().write.assert_called_once_with(b"a\r\nb\r\nc")


def test_convert_lf_to_crlf_lone_cr_message():
    data = b"a\rb\r\nc"
    counts, _ = analyze_line_endings_data(data)
    with patch("builtins.open", mock_open(read_data=b"a\rb\r\nc")), patch("builtins.print") as mock_print:
        convert_to_crlf("dummy.txt", issue_reason="contains lone CR line endings", data=data, counts=counts)
        mock_print.assert_any_call(
            "🟡 dummy.txt contains lone CR line endings and needs line endings replacement"
        )


def test_convert_lf_to_crlf_error():
    data = b"a\nb\nc"
    counts, _ = analyze_line_endings_data(data)
    with patch("builtins.open", side_effect=Exception("write error")):
        with pytest.raises(SystemExit):
            convert_to_crlf("dummy.txt", issue_reason="needs LF to CRLF conversion", data=data, counts=counts)


def test_convert_lf_to_crlf_mixed_endings_real_file(tmp_path):
    sample = Path(tmp_path) / "sample.txt"
    data = b"a\nb\rc\r\nd"
    sample.write_bytes(data)
    counts, _ = analyze_line_endings_data(data)
    convert_to_crlf(str(sample), issue_reason="contains lone CR line endings", data=data, counts=counts)
    assert sample.read_bytes() == b"a\r\nb\r\nc\r\nd"


def test_copy_file_success():
    with patch("os.makedirs") as mock_makedirs, patch("builtins.open", mock_open()) as mock_file:
        copy_file("source.txt", "destination.txt")
        mock_makedirs.assert_called_once()
        mock_file.assert_called()


def test_copy_file_error():
    with patch("builtins.open", side_effect=Exception("File error")), patch("builtins.print") as mock_print:
        copy_file("source.txt", "destination.txt")
        print(mock_print.call_args_list)  # Debug: Print all calls to mock_print
