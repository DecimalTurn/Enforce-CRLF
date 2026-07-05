import os
import argparse
import sys


def analyze_line_endings_data(data):
    counts = {
        "LF": 0,
        "CRLF": 0,
        "CR": 0,
    }

    index = 0
    while index < len(data):
        byte = data[index]
        if byte == ord('\r'):
            if index + 1 < len(data) and data[index + 1] == ord('\n'):
                counts["CRLF"] += 1
                index += 2
            else:
                counts["CR"] += 1
                index += 1
        elif byte == ord('\n'):
            counts["LF"] += 1
            index += 1
        else:
            index += 1

    present_labels = [name for name in ("LF", "CRLF", "CR") if counts[name] > 0]
    if not present_labels:
        label = None
    elif len(present_labels) == 1:
        label = present_labels[0]
    else:
        label = f"Mixed ({' + '.join(present_labels)})"

    return counts, label


def analyze_line_endings(filepath):
    with open(filepath, 'rb') as file:
        data = file.read()

    return analyze_line_endings_data(data)


def analyze_file(filepath):
    with open(filepath, 'rb') as file:
        data = file.read()

    counts, label = analyze_line_endings_data(data)
    issue_reason = get_line_endings_issue_from_analysis(counts, label)
    return {
        "data": data,
        "counts": counts,
        "label": label,
        "issue_reason": issue_reason,
    }


def get_line_endings_issue_from_analysis(counts, label):
    if counts["CR"] > 0:
        return "contains lone CR line endings"

    if label is None or label == "CRLF":
        return None

    if label.startswith("Mixed"):
        return f"contains mixed line endings: {label}"

    if label == "LF":
        return "needs LF to CRLF conversion"

    return f"contains {label} line endings"


def get_line_endings_issue(filepath, analysis=None):
    if analysis is None:
        analysis = analyze_file(filepath)
    return analysis["issue_reason"]


def convert_to_crlf(filepath, issue_reason, data, counts):
    try:
        if issue_reason:
            print(f"🟡 {filepath} {issue_reason} and needs line endings replacement")
        else:
            print(f"🟡 {filepath} needs line endings replacement")

        output_size = len(data) + counts["LF"] + counts["CR"]
        converted = bytearray(output_size)

        index = 0
        output_index = 0
        while index < len(data):
            byte = data[index]
            if byte == ord('\r'):
                if index + 1 < len(data) and data[index + 1] == ord('\n'):
                    converted[output_index] = ord('\r')
                    converted[output_index + 1] = ord('\n')
                    output_index += 2
                    index += 2
                else:
                    converted[output_index] = ord('\r')
                    converted[output_index + 1] = ord('\n')
                    output_index += 2
                    index += 1
            elif byte == ord('\n'):
                converted[output_index] = ord('\r')
                converted[output_index + 1] = ord('\n')
                output_index += 2
                index += 1
            else:
                converted[output_index] = byte
                output_index += 1
                index += 1

        with open(filepath, 'wb') as file:
            file.write(converted)

        print(f"    🟢 {filepath} had their line endings replaced")
    except Exception as e:
        print(f"🔴 {filepath} returned an error while converting: {e}")
        sys.exit(1)


def copy_file(source, destination):
    try:
        # Ensure the destination directory exists
        destination_dir = os.path.dirname(destination)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        # Open the source file for reading
        with open(source, 'rb') as source_file:
            # Create the destination file and write the contents of the source file to it
            with open(destination, 'wb') as destination_file:
                destination_file.write(source_file.read())
        print(f"File '{source}' copied to '{destination}' successfully.")
    except Exception as e:
        print(f"An error occurred while copying the file: {e}")


def main(extensions, fail_on_lf=False):
    repo_dir = "/home/runner/work/"
    # Split the extensions string into a list and strip whitespace
    extensions_list = tuple(ext.strip() for ext in extensions.split(','))
    files = []
    files_needing_conversion = []
    for root, _, filenames in os.walk(repo_dir):
        for filename in filenames:
            if filename.endswith(extensions_list):
                filepath = os.path.join(root, filename)
                files.append(filepath)

                analysis = analyze_file(filepath)
                issue_reason = analysis["issue_reason"]

                if issue_reason:
                    files_needing_conversion.append((filepath, issue_reason))
                    if not fail_on_lf:
                        convert_to_crlf(
                            filepath,
                            issue_reason=issue_reason,
                            data=analysis["data"],
                            counts=analysis["counts"],
                        )
                    else:
                        print(f"🔴 {filepath} {issue_reason} and needs line endings replacement")
                else:
                    print(f"🟢 {filepath} has correct line endings")

    if not files:
        print("No files with the specified extensions found in the repository.")
    else:
        print(f"Found {len(files)} file(s) with the specified extensions.")

    if fail_on_lf and files_needing_conversion:
        print(f"\n🔴 {len(files_needing_conversion)} file(s) need CRLF conversion:")
        for f, issue_reason in files_needing_conversion:
            print(f"  - {f}: {issue_reason}")
        sys.exit(2)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process files with specified extensions in a directory.")
    parser.add_argument('--extensions', type=str, required=True,
                        help='Comma-separated list of file extensions to process')
    parser.add_argument('--fail-on-lf', type=str, default="false",
                        help='Fail if files need CRLF conversion (true/false)')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    fail_on_lf = str(args.fail_on_lf).lower() == "true"
    main(args.extensions, fail_on_lf=fail_on_lf)
