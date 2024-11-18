import os

file_absolute_path = input('Enter the absolute path to your file: ')

print(os.stat(file_absolute_path).st_ctime_ns)
print(os.stat(file_absolute_path).st_mtime_ns)