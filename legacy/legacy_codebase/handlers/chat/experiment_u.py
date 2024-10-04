import magic


def get_mime_type(file_content):
    m = magic.Magic(mime=True)
    return m.from_buffer(file_content)


file_content = b'asdadasdas\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x00\x00'
mime_type = get_mime_type(file_content)

print("Тип MIME файла:", mime_type)
