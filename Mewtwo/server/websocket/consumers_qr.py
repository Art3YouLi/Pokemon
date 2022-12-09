from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from server.lib.qr_context import get_context

#  获得一个环境变量
qrContext = get_context()


class QrConsumer(WebsocketConsumer):
    """
    扫码进度websocket
    """

    def connect(self):
        self.room_group_name = 'qr%s' % bytes.decode(self.scope['query_string'])
        self.channel_name = 'qr_cn%s' % bytes.decode(self.scope['query_string'])
        print(self.room_group_name)
        print(self.channel_name)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send(text_data=self.channel_name)
        qrContext.add(self.channel_name, self)

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        qrContext.remove(self.channel_name)
        print('close')

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                # chat_message 方法
                'type': 'chat_message',
                'message': '成功获得二维码'
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=message)

    def sed_text(self, text):
        self.send(text_data=text)
