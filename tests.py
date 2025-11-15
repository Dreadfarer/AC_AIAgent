from functions.config import *
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content

def test():
    result = get_file_content("calculator", "lorem.txt")
    print("Result for current file:")
    print(result)
    print("")



if __name__ == "__main__":
    test()