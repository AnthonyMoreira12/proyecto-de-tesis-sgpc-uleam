from rest_framework.parsers import FormParser, MultiPartParser


class PublicacionesMultiPartMixin:
    parser_classes = [MultiPartParser, FormParser]