from setuptools import setup
from sys import argv

if __name__ == "__main__":
    if len(argv) < 2:
        raise Exception(
            "\n".join([
                "Need to pass the command you want to run.",
                "Example: `python -m ingenii_data_engineering "
                "pre_processing_package pre_process`"
            ])
        )
    command = argv[1]

    if command != "pre_processing_package":
        raise Exception(
            f"Don't recognise command {command}. The only command we recognise"
            " is pre_processing_package"
        )

    # Folder name can be passed as the second parameter
    # If not, assume the folder is called 'pre_process'
    if len(argv) == 2:
        folder_name = "pre_process"
    else:
        folder_name = argv[2]

    setup(
        name="pre_process",
        version="1.0.0",
        author="Internal",
        packages=[folder_name],
        description="Package containing pre-processing scripts",
        script_args=["bdist_wheel"]
    )
