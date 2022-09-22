# api_yandb/api/viewsets.py
from rest_framework import mixins, viewsets


class GetPatchUserViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    pass
