import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from enforce_crlf import (
    analyze_line_endings_data,
    convert_to_crlf,
    copy_file,
    main,
)


def test_analyze_line_endings_data_crlf_only():
    counts, eol_status = analyze_line_endings_data(b"a\r\nb\r\nc")
    assert counts == {"LF": 0, "CRLF": 2, "CR": 0}
    assert eol_status == "CRLF"


def test_analyze_line_endings_data_mixed_lf_crlf():
    counts, eol_status = analyze_line_endings_data(b"a\nb\r\nc")
    assert counts == {"LF": 1, "CRLF": 1, "CR": 0}
    assert eol_status == "Mixed (LF + CRLF)"


def test_analyze_line_endings_data_mixed_all_three():
    counts, eol_status = analyze_line_endings_data(b"a\nb\r\nc\rd")
    assert counts == {"LF": 1, "CRLF": 1, "CR": 1}
    assert eol_status == "Mixed (LF + CRLF + CR)"


def test_analyze_line_endings_data_no_terminators():
    counts, eol_status = analyze_line_endings_data(b"abc")
    assert counts == {"LF": 0, "CRLF": 0, "CR": 0}
    assert eol_status == "NONE"


def test_analyze_line_endings_data_lf_only():
    counts, eol_status = analyze_line_endings_data(b"a\nb\nc")
    assert counts == {"LF": 2, "CRLF": 0, "CR": 0}
    assert eol_status == "LF"


def test_analyze_line_endings_data_cr_only():
    counts, eol_status = analyze_line_endings_data(b"a\rb\rc")
    assert counts == {"LF": 0, "CRLF": 0, "CR": 2}
    assert eol_status == "CR"


def test_analyze_line_endings_data_lone_cr_and_crlf_is_mixed():
    counts, eol_status = analyze_line_endings_data(b"a\rb\r\nc")
    assert counts == {"LF": 0, "CRLF": 1, "CR": 1}
    assert eol_status == "Mixed (CRLF + CR)"


def test_convert_lf_to_crlf_success():
    data = b"a\nb\nc"
    counts, _ = analyze_line_endings_data(data)
    with patch("builtins.open", mock_open(read_data=b"a\nb\nc")) as mocked_open:
        convert_to_crlf("dummy.txt", data=data, counts=counts)
        mocked_open().write.assert_called_once_with(b"a\r\nb\r\nc")


def test_convert_to_crlf_success_message():
    data = b"a\rb\r\nc"
    counts, _ = analyze_line_endings_data(data)
    with patch("builtins.open", mock_open(read_data=b"a\rb\r\nc")), patch("builtins.print") as mock_print:
        convert_to_crlf("dummy.txt", data=data, counts=counts)
        mock_print.assert_any_call(
            "    🟢 dummy.txt had all their line endings replaced with CRLF"
        )


def test_convert_lf_to_crlf_error():
    data = b"a\nb\nc"
    counts, _ = analyze_line_endings_data(data)
    with patch("builtins.open", side_effect=Exception("write error")):
        with pytest.raises(SystemExit):
            convert_to_crlf("dummy.txt", data=data, counts=counts)


def test_convert_lf_to_crlf_mixed_endings_real_file(tmp_path):
    sample = Path(tmp_path) / "sample.txt"
    data = b"a\nb\rc\r\nd"
    sample.write_bytes(data)
    counts, _ = analyze_line_endings_data(data)
    convert_to_crlf(str(sample), data=data, counts=counts)
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


def test_main_none_status_does_not_convert():
    with patch("enforce_crlf.os.walk", return_value=[("/home/runner/work/", [], ["a.bas"])]), \
            patch("builtins.open", mock_open(read_data=b"abc")), \
            patch("enforce_crlf.convert_to_crlf") as mock_convert, \
            patch("builtins.print") as mock_print:
        main(".bas", fail_on_lf=False)

    mock_convert.assert_not_called()
    mock_print.assert_any_call("🟢 /home/runner/work/a.bas has correct line endings")


def test_main_fail_on_lf_exits_with_status_2():
    with patch("enforce_crlf.os.walk", return_value=[("/home/runner/work/", [], ["a.bas"])]), \
            patch("builtins.open", mock_open(read_data=b"a\nb\n")), \
            patch("builtins.print") as mock_print:
        with pytest.raises(SystemExit) as exc:
            main(".bas", fail_on_lf=True)

    assert exc.value.code == 2
    mock_print.assert_any_call("🔴 /home/runner/work/a.bas has LF line endings and needs line endings replacement")


def test_main_autofix_passes_data_and_counts_to_converter():
    data = b"a\nb\r\nc"
    expected_counts, _ = analyze_line_endings_data(data)

    with patch("enforce_crlf.os.walk", return_value=[("/home/runner/work/", [], ["a.bas"])]), \
            patch("builtins.open", mock_open(read_data=data)), \
            patch("enforce_crlf.convert_to_crlf") as mock_convert:
        main(".bas", fail_on_lf=False)

    mock_convert.assert_called_once_with(
        "/home/runner/work/a.bas",
        data=data,
        counts=expected_counts,
    )


def test_main_no_matching_files_message():
    with patch("enforce_crlf.os.walk", return_value=[("/home/runner/work/", [], ["a.txt"])]), \
            patch("builtins.print") as mock_print:
        main(".bas", fail_on_lf=False)

    mock_print.assert_any_call("No files with the specified extensions found in the repository.")
