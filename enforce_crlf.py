import os
import argparse
import sys
import subprocess


def needs_conversion_to_crlf(filepath):
    file_info = subprocess.check_output(['file', filepath], universal_newlines=True)
    if ", with no line terminators" in file_info or file_info.endswith("empty\n"):
        return False
    return ", with CRLF line terminators" not in file_info


def convert_lf_to_crlf(filepath):
    try:
        # Use the subprocess module to run the todos (aka. unix2dos) command
        print(f"🟡 {filepath} needs line endings replacement")
        subprocess.run(["todos", filepath], check=True)
        print(f"    🟢 {filepath} had there line endings replaced")
    except subprocess.CalledProcessError as e:
        print(f"🔴 {filepath} returned an error while converting: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("⚠ Error: todos command not found. Make sure it's installed and in your PATH.")
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

                eol_result = needs_conversion_to_crlf(filepath)
                if eol_result:
                    files_needing_conversion.append(filepath)
                    if not fail_on_lf:
                        convert_lf_to_crlf(filepath)
                    else:
                        print(f"🔴 {filepath} needs line endings replacement")
                else:
                    print(f"🟢 {filepath} has correct line endings")

    if not files:
        print("No files with the specified extensions found in the repository.")
    else:
        print(f"Found {len(files)} file(s) with the specified extensions.")

    if fail_on_lf and files_needing_conversion:
        print(f"\n🔴 {len(files_needing_conversion)} file(s) need CRLF conversion:")
        for f in files_needing_conversion:
            print(f"  - {f}")
        sys.exit(2)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process files with specified extensions in a directory.")
    parser.add_argument('--extensions', type=str, required=True, help='Comma-separated list of file extensions to process')
    parser.add_argument('--fail-on-lf', type=str, default="false", help='Fail if files need CRLF conversion (true/false)')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    fail_on_lf = str(args.fail_on_lf).lower() == "true"
    main(args.extensions, fail_on_lf=fail_on_lf)
