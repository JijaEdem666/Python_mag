import cv2
import os

class OutputFileExistsError(FileExistsError):

    def __init__(self, file_path):
        self.file_path = file_path
        super().__init__(f"Файл уже существует и не может быть перезаписан: {file_path}")

def make_unique_path(file_path):

    if not os.path.exists(file_path):
        return file_path, False

    base, ext = os.path.splitext(file_path)
    i = 1
    while True:
        candidate = f'{base}_{i}{ext}'
        if not os.path.exists(candidate):
            return candidate, True
        i += 1

def write_data(file_path, data):
    try:
        new_file_path, redacted = make_unique_path(file_path)
        if redacted:
            raise OutputFileExistsError(file_path)
    except OutputFileExistsError as e:
        print(f'Ошибка: {e}')
        print(f'Новое имя файла сохранения: {new_file_path}')
    cv2.imwrite(new_file_path, data)