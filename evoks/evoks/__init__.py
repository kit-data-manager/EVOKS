# import os
# from mypy import api
# from sty import fg # type: ignore

# py_files = []
# for root, dirs, files in os.walk("."):
#     for file in files:
#         if file.endswith(".py"):
#             py_files.append(os.path.join(root, file))

# result = api.run(py_files)

# if result[0]:
#     print(fg.red + 'Type checking report:' + fg.rs)
#     print(result[0])  # stdout

# if result[1]:
#     print(fg.red + 'Error report:' + fg.rs)
#     print(result[1])  # stderr

# print('\nExit status:', result[2])
