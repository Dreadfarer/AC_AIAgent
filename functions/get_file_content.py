import os
from config import MAX_CHARS
from google.genai import types

def get_file_content(working_directory, file_path):
    """
    Reads the content of a file located at the specified path within the given working directory.
    Args:
        working_directory (str): The base directory where the file is located.
        file_path (str): The relative path to the file from the working directory.
    Returns:
        str: The content of the file as a string.
    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there is an error reading the file.
    """

    abs_working_dir = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(abs_working_dir, file_path))
    if os.path.commonpath([abs_working_dir, target_file]) != abs_working_dir:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(target_file, 'r') as file:
            content = file.read()
            if len(content) > MAX_CHARS:
                return content[:MAX_CHARS] + f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            return content
        
    except Exception as e:
        return f"Error reading file: {e}"

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the content of a specified file within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The relative path to the file from the working directory.",
            ),
        },
    ),
)