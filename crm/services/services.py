from datetime import datetime, timedelta
from itertools import chain
from operator import attrgetter
import os


from dotenv import load_dotenv
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll

from crm.models import Order, Address, Customer
from core.settings import BASE_DIR

dotenv_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Message:
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def get_my_model_name(self):
        return self.__class__.__name__


def get_object_from_db(model, pk):
    """Возвращает объект из базы данных"""
    return model.objects.filter(pk=pk)


def get_comments_for_object(obj):
    """Возвращает все комментарии для объекта"""
    return obj.comments.all()


def get_tasks_for_object(obj):
    """Возвращает все комментарии для объекта"""
    return obj.tasks.all()


def get_customer_orders(customer_id):
    return Order.objects.filter(customer_id=customer_id)


def get_customer_addresses(customer_id):
    return Address.objects.filter(
        customer=Customer.objects.get(pk=customer_id))


def get_all_context(*args):
    return sorted(chain(*args), key=attrgetter('date'), reverse=True)[::-1]


def convert_list_to_message_obj(list_for_convert):
    return [Message(**message) for message in list_for_convert]


def get_context_comm_window(model, pk):
    context_obj = get_object_from_db(model, pk)
    current_obj = context_obj.get()
    vk = Vkontakte()
    if current_obj.get_my_model_name() != 'customer':
        curent_customer = current_obj.customer
    else:
        curent_customer = current_obj
    try:
        history = vk.get_history_message(
            curent_customer.social_web.get(name_social=1), 10)
    except:
        history = []
    context = get_all_context(
        convert_list_to_message_obj(history),
        get_comments_for_object(current_obj),
        get_tasks_for_object(current_obj),
        get_object_from_db(model, pk),
        get_customer_orders(pk) if current_obj.get_my_model_name() == 'customer' else []

    )
    dates_context = sorted(set(content.date.date() for content in context))
    return {'context': context, 'dates_context': dates_context}


class AuthenticationVkontakte:
    __vk_user_token = os.environ.get("VK_USER_TOKEN")
    __vk_group_token = os.environ.get("VK_GROUP_TOKEN")

    @property
    def get_user_token(self):
        return self.__vk_user_token

    @property
    def get_group_token(self):
        return self.__vk_group_token


class Vkontakte:
    __auth = AuthenticationVkontakte()

    @property
    def __get_vk_session(self):
        return vk_api.VkApi(token=self.__auth.get_group_token)

    @property
    def _get_vk_group_api(self):
        return self.__get_vk_session.get_api()

    @property
    def _get_group_message(self):
        return self._get_vk_group_api.messages

    @property
    def get_group_conversations(self):
        return self._get_group_message.getConversations(extended=1)

    def get_history_message(self, id_user, count=200):
        messages = self._get_group_message.getHistory(user_id=id_user,
                                                      count=count)['items']
        update_message = []
        for message in messages:
            message['date'] = datetime.utcfromtimestamp(
                message['date']) + timedelta(hours=3)
            update_message.append(message)
        return update_message

    def get_info_user(self, vk_id):
        return self._get_vk_group_api.users.get(user_ids=vk_id)





