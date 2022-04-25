import channels.layers
from asgiref.sync import async_to_sync
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet

from core.blocks.consumers import BlockConsumer

from ..models.block import Block
from ..serializers.block import BlockSerializer, BlockSerializerCreate


def send(block_data):
    channel_layer = channels.layers.get_channel_layer()
    payload = {'type': 'send.block', 'message': block_data}
    async_to_sync(channel_layer.group_send)(BlockConsumer.group_name(block_data['recipient']), payload)


class BlockViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    # TODO(dmu) MEDIUM: Why do we need `filterset_fields` given that `filter_backends` is not set?
    filterset_fields = ('amount', 'recipient', 'sender')
    queryset = Block.objects.order_by('id').all()
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
        # TODO(dmu) MEDIUM: Consider not serializing the block again
        block_data = self.get_serializer(block).data

        send(block_data)

        return Response(block_data, status=HTTP_201_CREATED)
