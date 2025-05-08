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


def main(extensions):
    repo_dir = "/home/runner/work/"
    # Split the extensions string into a list and strip whitespace
    extensions_list = tuple(ext.strip() for ext in extensions.split(','))
    files = []
    for root, _, filenames in os.walk(repo_dir):
        for filename in filenames:
            if filename.endswith(extensions_list):
                filepath = os.path.join(root, filename)
                files.append(filepath)

                eol_result = needs_conversion_to_crlf(filepath)
                if eol_result:
                    convert_lf_to_crlf(filepath)
                else:
                    print(f"🟢 {filepath} has correct line endings")

    if not files:
        print("No files with the specified extensions found in the repository.")
    else:
        print(f"Found {len(files)} file(s) with the specified extensions.")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process files with specified extensions in a directory.")
    parser.add_argument('extensions', type=str, help='Comma-separated list of file extensions to process')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    main(args.extensions)
