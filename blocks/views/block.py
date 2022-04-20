from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet

from ..models.block import Block
from ..serializers.block import BlockSerializer, BlockSerializerCreate


class BlockViewSet(
    CreateModelMixin,
    GenericViewSet,
    ListModelMixin,
):
    filterset_fields = ['amount', 'recipient', 'sender']
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    serializer_create_class = BlockSerializerCreate

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_create_class(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        block = serializer.save()

        return Response(
            self.get_serializer(block).data,
            status=HTTP_201_CREATED,
        )
