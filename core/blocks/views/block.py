import channels.layers
from asgiref.sync import async_to_sync
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet

from core.blocks.consumers import BlockConsumer

from ..models.block import Block
from ..serializers.block import BlockSerializer, BlockSerializerCreate


class BlockViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    # TODO(dmu) MEDIUM: Why do we need `filterset_fields` given that `filter_backends` is not set?
    filterset_fields = ('amount', 'recipient', 'sender')
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    serializer_create_class = BlockSerializerCreate

    def create(self, request, *args, **kwargs):
        # TODO(dmu) MEDIUM: Use PerActionSerializerMixin instead of overriding create()
        serializer = self.serializer_create_class(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        block = serializer.save()
        block_data = self.get_serializer(block).data

        channel_layer = channels.layers.get_channel_layer()
        payload = {'type': 'send.block', 'message': block_data}
        async_to_sync(channel_layer.group_send)(BlockConsumer.group_name(block.recipient), payload)

        return Response(block_data, status=HTTP_201_CREATED)
