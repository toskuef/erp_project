import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'test'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        date = text_data_json['date']
        text = text_data_json['text']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'date': date,
                'text': text
            }
        )

    def chat_message(self, event):
        message = event['message']
        date = event['date']
        text = event['text']

        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
            'date': date,
            'text': text
        }))


class NewCustomer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'new_customer'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        cust = text_data_json['cust']
        status = text_data_json['status']
        source = text_data_json['source']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'new_customer',
                'cust': cust,
                'status': status,
                'source': source
            }
        )

    def new_customer(self, event):
        cust = event['cust']
        status = event['status']
        source = event['source']

        self.send(text_data=json.dumps({
            'type': 'new_customer',
            'cust': cust,
            'status': status,
            'source': source,

        }))

