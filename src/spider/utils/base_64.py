import base64

from django.core.files.base import ContentFile


class Base64:
    @staticmethod
    def to_file(data, name=None):
        _format, _img_str = data.split(";base64,")
        _name, ext = _format.split("/")
        if not name:
            name = _name.split(":")[-1]
        return ContentFile(base64.b64decode(_img_str), name="{}.{}".format(name, ext))

    @staticmethod
    def from_file(file_bytes, name="file", ext=""):
        _file_str = base64.b64encode(file_bytes)
        return "data:{}/{};base64,{}".format(name, ext, _file_str.decode("utf-8"))

    @staticmethod
    def from_file_path(path):
        file = path.split("/")[-1]
        try:
            name, ext = file.rsplit(".", 1)
        except:
            name = file
            ext = ""
        with open(path, "rb") as file:
            return Base64.from_file(file.read(), name, ext)
