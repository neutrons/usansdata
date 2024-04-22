# import standard
import os
from unittest.mock import MagicMock
from unittest.mock import patch as mock_patch

# third party packages
import pytest

# usansred imports
from usansred.reduce import main as reduceUSANS


def read_numbers_from_file(filename):
    """
    Read numbers from a file and return a list of lists, where each inner list contains the numbers from a line.
    """
    numbers_list = []
    with open(filename, "r") as file:
        for line in file:
            numbers = line.strip().split(",")
            numbers_list.append([float(num) for num in numbers if num])
    return numbers_list


def compare_lines(file1, file2, threshold=0.01):
    """
    Compare corresponding numbers in two files line by line.
    If the relative difference exceeds the threshold, print a warning.
    """
    numbers_list1 = read_numbers_from_file(file1)
    numbers_list2 = read_numbers_from_file(file2)

    for i, (line1, line2) in enumerate(zip(numbers_list1, numbers_list2), start=1):
        for num1, num2 in zip(line1, line2):
            try:
                relative_diff = abs(num1 - num2) / max(abs(num1), abs(num2))
            except ZeroDivisionError:
                pass
            if relative_diff > threshold:
                raise ValueError(f"Line {i}, Number {num1:.6f} differs significantly from {num2:.6f}")


@mock_patch("usansred.reduce.parse_arguments")
def test_main_nonvalid_file(mock_parse_arguments):
    # Setup mock objects
    mock_args = MagicMock()
    mock_args.logbin = False
    mock_args.path = "invalid_path.csv"
    mock_parse_arguments.return_value = mock_args
    with pytest.raises(FileNotFoundError) as error:
        reduceUSANS()
    assert str(error.value) == "The csv file invalid_path.csv doesn't exist"


@pytest.mark.datarepo()
@mock_patch("usansred.reduce.parse_arguments")
def test_main(mock_parse_arguments, data_server, tmp_path):
    # Setup mock objects
    mock_args = MagicMock()
    mock_args.logbin = False
    mock_args.path = data_server.path_to("setup.csv")
    mock_args.output = str(tmp_path)
    mock_parse_arguments.return_value = mock_args
    reduceUSANS()
    # compare the content of output files with files containing expected results
    goldendir = os.path.join(os.path.dirname(mock_args.path), "reduced")  # where the expected content resides
    names = ["EmptyPCell", "S115_dry", "S115_pc3"]
    suffixes = ["", "_lbs", "_lb", "_unscaled"]
    for name in names:
        for suffix in suffixes:
            filename = f"UN_{name}_det_1{suffix}.txt"
            output = os.path.join(tmp_path, filename)
            expected = os.path.join(goldendir, filename)
            if os.path.exists(expected):  # file "UN_EmptyPCell_det_1_lbs.txt" does not exist
                compare_lines(output, expected)


if __name__ == "__main__":
    pytest.main([__file__])
