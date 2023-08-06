def open_test_file(path):
    with open(path, "r", encoding="UTF-8") as file:
        return file.read().strip()
