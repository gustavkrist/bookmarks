import os
import tempfile


def prompt(choices=None, fzf_options="", delimiter="\n"):
    # convert lists to strings [ 1, 2, 3 ] => "1\n2\n3"
    choices_str = delimiter.join(map(str, choices))
    selection = []

    with tempfile.NamedTemporaryFile(delete=False) as input_file:
        with tempfile.NamedTemporaryFile(delete=False) as output_file:
            # Create an temp file with list entries as lines
            input_file.write(choices_str.encode("utf-8"))
            input_file.flush()

    # Invoke fzf externally and write to output file
    os.system(f'fzf {fzf_options} < "{input_file.name}" > "{output_file.name}"')

    # get selected options
    with open(output_file.name, encoding="utf-8") as f:
        for line in f:
            selection.append(line.strip("\n"))

    os.unlink(input_file.name)
    os.unlink(output_file.name)

    return selection
