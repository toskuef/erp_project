import json
import os
from datetime import datetime, timedelta
from itertools import chain
from operator import attrgetter

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Sum, Case, When, Max, Value, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView

import httplib2
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from vk_api import vk_api
from vk_api.utils import get_random_id

from core import settings
from crm.models import Customer, Comment, Task, AddressCountry, AddressArea, \
    AddressRegion, AddressTown, AddressStreet, Address, Order, Product, \
    SocialWebCustomers, SourceCustomer, Measuring, Project, Files
from .forms import CustomerForm, CommentForm, TaskForm, OrderForm, AddressForm, \
    CountryForm, AreaForm, RegionForm, TownForm, StreetForm, ProductForm, \
    MeasuringForm, ProjectForm

from .services.services import (
    get_context_comm_window,
    get_customer_orders,
    Vkontakte,
    get_customer_addresses)

group_token = '8f9048a4892d2b9a82f14827dea55306849825156c574ad52c9044718b64ee8f085dcdd983da5230d0dac'
ACTIONS = [['Комментарий', 'comment'], ['Задача', 'task'], ['VK', 'VK']]


class CustomerList(ListView):
    model = Customer
    template_name = 'crm/crm_customers.html'
    paginate_by = 10

    def get_queryset(self):
        unread = {}
        for dialog in Vkontakte().get_group_conversations['items']:
            try:
                if dialog['conversation']['unread_count']:
                    cust = Customer.objects.filter(
                        social_web__id_user=dialog['conversation']['peer'][
                            'id']).values('pk').get()['pk']
                    unread[cust] = \
                        dialog['conversation']['unread_count']
            except:
                continue

        customers = Customer.objects.annotate(
            num_task=Sum(Case(When(tasks__is_done=False, then=1))),
            last_update=(datetime.now() - Max('tasks__date'))).annotate(
            status=Case(When(is_show=False, then=Value('Неразобран')),
                        When(last_update=None, then=Value('Новый')),
                        When(num_task__gt=0,
                             then=Value('Есть активные задачи')),
                        When(last_update__gt=timedelta(days=10),
                             then=Value('Неактивный')),
                        default=Value('Нет активных задач')))
        search_query = self.request.GET.get('search', '')
        for c in customers:
            if c.pk in unread:
                c.unread = unread[c.pk]
        if search_query:
            return customers.filter(Q(last_name__iregex=search_query))
        return customers

    def get_context_data(self, *args, **kwargs):
        unread = {}
        for dialog in Vkontakte().get_group_conversations['items']:
            try:
                if dialog['conversation']['unread_count']:
                    cust = Customer.objects.filter(
                        social_web__id_user=dialog['conversation']['peer'][
                            'id']).values('pk').get()['pk']
                    unread[cust] = \
                        dialog['conversation']['unread_count']
            except:
                continue
        context = super().get_context_data(*args, **kwargs)
        context['form'] = CustomerForm
        context['unread'] = unread
        comments = Comment.objects.filter(is_show=False, to=self.request.user)
        tasks = Task.objects.filter(is_show=False, to=self.request.user)
        context['notification'] = sorted(chain(comments, tasks), key=attrgetter('date'), reverse=True)[::-1]
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = CustomerForm(request.POST)
            if form.is_valid():
                customer = form.save(commit=False)
                customer.creater_customer = request.user
                customer.save()
                return redirect('crm:crm_customers')
            return render(request, 'crm/crm_customers.html', {
                'object_list': Customer.objects.all(),
                'form': form,
                'show': 'show',
            })


def customer_list_filter(request):
    template_name = 'crm/includes/customer_list.html'
    filter = request.GET.values()
    object_list = Customer.objects.annotate(
        num_task=Sum(Case(When(tasks__is_done=False, then=1))),
        last_update=(datetime.now() - Max('tasks__date'))).annotate(
        status=Case(When(is_show=False, then=Value('Неразобран')),
                    When(last_update=None, then=Value('Новый')),
                    When(last_update__gt=timedelta(days=10),
                         then=Value('Неактивный')),
                    When(num_task__gt=0,
                         then=Value('Есть активные задачи')),
                    default=Value('Нет активных задач'))).filter(
        status__in=list(filter))
    return render(request, template_name, {'object_list': object_list})


class CustomerDetail(DetailView):
    model = Customer
    template_name = 'crm/crm_customer_detail.html'

    def get(self, request, *args, **kwargs):
        Customer.objects.filter(pk=self.kwargs['pk']).update(is_show=True)
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        Comment.objects.filter(is_show=False, to=self.request.user,
                               content_type=12,
                               object_id=self.kwargs['pk']).update(
            is_show=True)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer_id = self.kwargs['pk']
        context['new_comment'] = CommentForm
        context['new_task'] = TaskForm
        context['address_list'] = get_customer_addresses(customer_id)
        context['new_order'] = OrderForm
        context['actions'] = ACTIONS
        context['order_list'] = get_customer_orders(customer_id)
        context['select'] = 'comment'
        try:
            context['vk_id'] = SocialWebCustomers.objects.get(
                customer=customer_id,
                name_social=SourceCustomer.objects.get(pk=1))
        except:
            context['vk_id'] = 0
        comments = Comment.objects.filter(is_show=False, to=self.request.user)
        tasks = Task.objects.filter(is_show=False, to=self.request.user)
        context['notification'] = sorted(chain(comments, tasks),
                                         key=attrgetter('date'), reverse=True)[
                                  ::-1]
        context.update(get_context_comm_window(Customer, customer_id))
        return context

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            template = 'crm/includes/crm_communication_window.html'
            if 'title' in request.POST:
                form = OrderForm(request.POST)
                customer = self.kwargs.get('pk')
                form_add_customer = form.save(commit=False)
                form_add_customer.customer = Customer.objects.get(pk=customer)
                form.save()
                return redirect('crm:crm_customer_detail', pk=customer)
            if 'last_name' in request.POST:
                customer = self.kwargs.get('pk')
                instance = get_object_or_404(Customer, pk=customer)
                form = CustomerForm(request.POST, instance=instance)
                form.save()
                return redirect('crm:crm_customer_detail', pk=customer)
            if 'street_title' in request.POST:
                customer_id = self.kwargs.get('pk')
                customer = get_object_or_404(Customer, pk=customer_id)
                country = AddressCountry.objects.get_or_create(country_title=request.POST['country_title'])[0]
                area = AddressArea.objects.get_or_create(area_title=request.POST['area_title'])[0]
                region = AddressRegion.objects.get_or_create(region_title=request.POST['region_title'])[0]
                town = AddressTown.objects.get_or_create(town_title=request.POST['town_title'])[0]
                street = AddressStreet.objects.get_or_create(street_title=request.POST['street_title'])[0]
                if Address.objects.filter(customer=customer).exists():
                    instance = get_object_or_404(Address, customer=customer)
                    form = AddressForm(request.POST, instance=instance)
                else:
                    form = AddressForm(request.POST)
                address = form.save(commit=False)
                address.country = country
                address.area = area
                address.region = region
                address.town = town
                address.street = street
                cust = Customer.objects.get(pk=customer_id)
                address.save()
                address.customer.add(cust)
                address.save()
                return redirect('crm:crm_customer_detail', pk=1)
            customer = Customer.objects.get(pk=self.kwargs['pk'])
            if 'text' in request.POST:
                form = CommentForm(request.POST)
                comment = form.save(commit=False)
                comment.content_object = customer
                comment.staff = request.user
                comment.save()
                context = get_context_comm_window(Customer, self.kwargs['pk'])
                return render(request, template, context)
            if 'task' in request.POST:
                form = TaskForm(request.POST)
                task = form.save(commit=False)
                task.content_object = customer
                task.staff = request.user
                task.save()
                context = get_context_comm_window(Customer, self.kwargs['pk'])
                return render(request, template, context)
            if 'done_task' in request.POST:
                task_id = request.POST['done_task']
                Task.objects.filter(pk=task_id).update(is_done=True)
                return redirect('crm:crm_customer_detail',
                                pk=self.kwargs['pk'])
            if 'vk' in request.POST:
                answer = request.POST['vk']
                vk_session = vk_api.VkApi(token=group_token)
                vk = vk_session.get_api()
                vk.messages.send(
                    user_id=customer.social_web.get(name_social=1),
                    random_id=get_random_id(),
                    message=answer
                )
                context = get_context_comm_window(Customer, self.kwargs['pk'])
                return render(request, template, context)

    def render_new_message(self):
        request = self.request
        template = 'crm/includes/crm_communication_window.html'
        context = get_context_comm_window(Customer, self.kwargs['pk'])
        return render(request, template, context)


def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(instance=customer)
    context = {'customer': customer, 'edit_customer': form}
    template_name = 'crm/crm_customer_edit.html'
    return render(request, template_name, context)


def address_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if Address.objects.filter(customer=customer).exists():
        address = Address.objects.get(customer=customer)
        address_form = AddressForm(instance=address)
        country_form = CountryForm(instance=AddressCountry.objects.get(addresses=address))
        area_form = AreaForm(instance=AddressArea.objects.get(addresses=address))
        region_form = RegionForm(instance=AddressRegion.objects.get(addresses=address))
        town_form = TownForm(instance=AddressTown.objects.get(addresses=address))
        street_form = StreetForm(instance=AddressStreet.objects.get(addresses=address))
    else:
        address_form = AddressForm
        country_form = CountryForm
        area_form = AreaForm
        region_form = RegionForm
        town_form = TownForm
        street_form = StreetForm
    country = AddressCountry.objects.all()
    area = AddressArea.objects.all()
    region = AddressRegion.objects.all()
    town = AddressTown.objects.all()
    street = AddressStreet.objects.all()
    context = {'customer': customer,
               'address_form': address_form,
               'country_form': country_form,
               'area_form': area_form,
               'region_form': region_form,
               'town_form': town_form,
               'street_form': street_form,
               'country': country,
               'area': area,
               'region': region,
               'town': town,
               'street': street}
    template_name = 'crm/crm_address_edit.html'
    return render(request, template_name, context)


def get_form_communication(request):
    if request.method == 'GET':
        templates = {
            'comment': 'crm/includes/crm_form_communication/crm_comment.html',
            'task': 'crm/includes/crm_form_communication/crm_task.html',
            'VK': 'crm/includes/crm_form_communication/crm_vk.html'}
        action = request.GET['action']
        if action == 'comment':
            return render(request, templates[action],
                          {'new_comment': CommentForm})
        if action == 'task':
            return render(request, templates[action], {'new_task': TaskForm})
        if action == 'VK':
            return render(request, templates[action])


class OrderDetail(DetailView):
    model = Order
    template_name = 'crm/crm_order_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        Comment.objects.filter(is_show=False, to=self.request.user,
                               content_type=15,
                               object_id=self.kwargs['pk']).update(
            is_show=True)

        # if self.request.GET.get('gsheet', ''):
        #     CREDENTIALS_FILE = os.path.join(settings.BASE_DIR,
        #                                     'toskins-0a3491bf4bd5.json')
        #     credentials = ServiceAccountCredentials.from_json_keyfile_name(
        #         CREDENTIALS_FILE,
        #         ['https://www.googleapis.com/auth/spreadsheets',
        #          'https://www.googleapis.com/auth/drive'])
        #     httpAuth = credentials.authorize(httplib2.Http())
        #     service = discovery.build('sheets', 'v4', http=httpAuth)
        #     driveService = discovery.build('drive', 'v3', http=httpAuth)
        #
        #     spreadsheetId = '1jZ_2BpSBVQAFN_9mJ_hTDKNsiUitekNGJVf1z6Lvsls'
        #     row = len(
        #         service.spreadsheets().values().get(
        #             spreadsheetId=spreadsheetId,
        #             range='RMP!A:K').execute().get(
        #             'values', [])) + 1
        #
        #     customer = Customer.objects.values('last_name', 'first_name',
        #                                        'family_name').get(
        #         pk=self.object.customer.pk)
        #     fio = ' '.join([customer['last_name'], customer['first_name'],
        #                     customer['family_name']])
        #
        #     num_order = Order.objects.values('pk').get(pk=self.kwargs['pk'])[
        #         'pk']
        #     title = Order.objects.values('title').get(pk=self.kwargs['pk'])[
        #         'title']
        #     date = Order.objects.values('date').get(pk=self.kwargs['pk'])[
        #         'date']
        #     date_done = \
        #     Order.objects.values('date_done').get(pk=self.kwargs['pk'])[
        #         'date_done']
        #     price = Order.objects.values('price').get(pk=self.kwargs['pk'])[
        #         'price']
        #     pre_pay = \
        #     Order.objects.values('pre_pay').get(pk=self.kwargs['pk'])[
        #         'pre_pay']
        #     pre_pay_type = \
        #     Order.objects.values('pre_pay_type').get(pk=self.kwargs['pk'])[
        #         'pre_pay_type']
        #
        #     data = [str(fio),
        #             str(num_order),
        #             str(date),
        #             str(title),
        #             str(date_done),
        #             str(price),
        #             str(pre_pay),
        #             str(pre_pay_type)]
        #     results = service.spreadsheets().values().batchUpdate(
        #         spreadsheetId=spreadsheetId, body={
        #             "valueInputOption": "USER_ENTERED",
        #             # Данные воспринимаются, как вводимые пользователем (считается значение формул)
        #             "data": [
        #                 {"range": f"RMP!A{row}:K{row}",
        #                  "majorDimension": "ROWS",
        #                  # Сначала заполнять строки, затем столбцы
        #                  "values": [data]}
        #             ]
        #         }).execute()


        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(OrderDetail, self).get_context_data(**kwargs)
        order = Order.objects.get(pk=self.kwargs['pk'])
        order_id = self.kwargs['pk']
        context['tasks'] = order.tasks.all()
        context['comments'] = order.comments.all()
        context['new_comment'] = CommentForm
        context['new_task'] = TaskForm
        context['new_product'] = ProductForm
        context['products'] = Product.objects.filter(order=self.kwargs['pk'])
        comments = Comment.objects.filter(is_show=False, to=self.request.user)
        tasks = Task.objects.filter(is_show=False, to=self.request.user)
        context['notification'] = sorted(chain(comments, tasks),
                                         key=attrgetter('date'), reverse=True)[
                                  ::-1]
        # context['actions'] = ACTIONS
        # context.update(get_context_comm_window(Order, order_id))
        return context

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            template = 'crm/includes/crm_communication_window.html'
            order = Order.objects.get(pk=self.kwargs['pk'])
            if 'text' in request.POST:
                form = CommentForm(request.POST)
                comment = form.save(commit=False)
                comment.content_object = order
                comment.staff = request.user
                comment.save()
                context = {}
                # context = get_context_comm_window(Order, self.kwargs['pk'])
                return render(request, template, context)
            if 'task' in request.POST:
                print(request.POST)
                form = TaskForm(request.POST)
                task = form.save(commit=False)
                task.content_object = order
                task.staff = request.user
                task.save()
                return redirect('crm:crm_order_detail', pk=self.kwargs['pk'])
            if 'title' in request.POST:
                form = ProductForm(request.POST)
                product = form.save(commit=False)
                product.order = order
                product.save()
                return redirect('crm:crm_order_detail', pk=self.kwargs['pk'])
            if 'status_order' in request.POST:
                Order.objects.filter(pk=self.kwargs['pk']).update(
                    status_order=3)
                products = Product.objects.filter(order=order)
                # product_in_product_order = [ProductOrder(
                #     name=product,
                #     is_active=True,
                #     is_specification_done=False
                # ) for product in products]
                # ProductOrder.objects.bulk_create(product_in_product_order)
                return redirect('crm:crm_order_detail', pk=self.kwargs['pk'])


def done_task(request, cust_pk, pk, object):
    Task.objects.filter(pk=pk).update(is_done=True)
    template = 'crm/includes/crm_communication_window.html'
    if object == 'customer':
        context = get_context_comm_window(Customer, cust_pk)
    else:
        context = get_context_comm_window(Order, cust_pk)
    return render(request, template, context)


def start_task(request, pk, cust_pk, object):
    Task.objects.filter(pk=pk).update(is_show=True)
    template = 'crm/includes/crm_communication_window.html'
    if object == 'customer':
        context = get_context_comm_window(Customer, cust_pk)
    else:
        context = get_context_comm_window(Order, cust_pk)
    return render(request, template, context)


@csrf_exempt
def vk(request):
    if request.method == 'POST':
        event = json.loads(request.body)
        if event['type'] == 'message_new':
            obj_message = event['object']['message']
            vk_id = str(obj_message['from_id'])
            channel_layer = get_channel_layer()
            if SocialWebCustomers.objects.filter(name_social=1,
                                                 id_user=vk_id).exists():
                text = str(obj_message['text'])
                date = int(obj_message['date'])
                date = datetime.utcfromtimestamp(date) + timedelta(hours=3)
                async_to_sync(channel_layer.group_send)(
                    'test',
                    {
                        'type': 'chat_message',
                        'message': f'{text}',
                        'date': f'{date}',
                        'text': f'text_mess'
                    }
                )
            else:
                new_user = Vkontakte().get_info_user(vk_id=vk_id)[0]
                new_customer = Customer.objects.create(
                    last_name=new_user['last_name'],
                    first_name=new_user['first_name'],
                    source=SourceCustomer.objects.get(pk=1))
                SocialWebCustomers.objects.create(customer=new_customer,
                                                  name_social=SourceCustomer.objects.get(
                                                      pk=1),
                                                  id_user=vk_id)
                pk = new_customer.pk
                async_to_sync(channel_layer.group_send)(
                    'new_customer',
                    {
                        'type': 'new_customer',
                        'cust': f'{new_customer}',
                        'status': f'{pk}',
                        'source': f'Вконтакте'
                    }
                )
        return HttpResponse('ok')


class Search(ListView):
    model = Customer
    template_name = 'crm/crm_search_list.html'

    def get_queryset(self):
        unread = {}
        for dialog in Vkontakte().get_group_conversations['items']:
            try:
                if dialog['conversation']['unread_count']:
                    cust = Customer.objects.filter(
                        social_web__id_user=dialog['conversation']['peer'][
                            'id']).values('pk').get()['pk']
                    unread[cust] = \
                        dialog['conversation']['unread_count']
            except:
                continue

        customers = Customer.objects.annotate(
            num_task=Sum(Case(When(tasks__is_done=False, then=1))),
            last_update=(datetime.now() - Max('tasks__date'))).annotate(
            status=Case(When(is_show=False, then=Value('Неразобран')),
                        When(last_update=None, then=Value('Новый')),
                        When(last_update__gt=timedelta(days=10),
                             then=Value('Неактивный')),
                        When(num_task__gt=0,
                             then=Value('Есть активные задачи')),
                        default=Value('Нет активных задач'))).all()
        search_query = self.request.GET.get('search', '')
        for c in customers:
            if c.pk in unread:
                c.unread = unread[c.pk]
        if search_query:
            return customers.filter(Q(last_name__iregex=search_query))
        return customers

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        search_query = self.request.GET.get('search', '')
        orders = Order.objects.filter(Q(title__iregex=search_query) | Q(
            customer__last_name__iregex=search_query) | Q(
            customer__first_name__iregex=search_query) | Q(
            customer__family_name__iregex=search_query))
        customers = Customer.objects.filter(Q(last_name__iregex=search_query))
        products = Product.objects.filter(Q(title__iregex=search_query))
        search_list = list(chain(orders, customers, products))
        context['search_list'] = search_list
        comments = Comment.objects.filter(is_show=False, to=self.request.user)
        tasks = Task.objects.filter(is_show=False, to=self.request.user)
        context['notification'] = sorted(chain(comments, tasks),
                                         key=attrgetter('date'), reverse=True)[
                                  ::-1]
        return context


class ProductDetail(DetailView):
    model = Product
    template_name = 'crm/crm_product_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        context['new_measuring'] = MeasuringForm
        context['new_project'] = ProjectForm
        context['measurings'] = Measuring.objects.filter(
            product=self.kwargs['pk'])
        context['projects'] = Project.objects.filter(
            product=self.kwargs['pk'])
        comments = Comment.objects.filter(is_show=False, to=self.request.user)
        tasks = Task.objects.filter(is_show=False, to=self.request.user)
        context['notification'] = sorted(chain(comments, tasks),
                                         key=attrgetter('date'), reverse=True)[
                                  ::-1]
        context['files'] = Files.objects.filter(product_id=self.kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            if 'measuring' in request.FILES:
                form = MeasuringForm(request.POST, request.FILES)
                measuring = form.save(commit=False)
                measuring.product = Product.objects.get(pk=self.kwargs['pk'])
                measuring.save()
                return redirect('crm:crm_product_detail', pk=self.kwargs['pk'])
            if 'project' in request.FILES:
                form = ProjectForm(request.POST, request.FILES)
                project = form.save(commit=False)
                project.product = Product.objects.get(pk=self.kwargs['pk'])
                project.save()
                return redirect('crm:crm_product_detail', pk=self.kwargs['pk'])


def add_file(request, pk, object):
    CREDENTIALS_FILE = os.path.join(settings.BASE_DIR,
                                    'toskins-0a3491bf4bd5.json')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = discovery.build('sheets', 'v4', http=httpAuth)
    driveService = discovery.build('drive', 'v3', http=httpAuth)

    prod = Product.objects.get(pk=pk)
    ord = Order.objects.get(products=prod)
    cust = Customer.objects.get(orders=ord)

    if object == 'rs':
        sh_price = '1deqUBgXTOnAqZNklsAhqCJcx5p68FfrHpopKJHT7Jhw'
        folder = '1-5Qscphr4n_hGPGGnLFkO84LD2pjicP0'
        newfile = {'name': f'Расчет ({datetime.now().date()}): {str(cust)} - {str(prod)}',
                   'parents': [folder]}
        new_price = driveService.files().copy(
            fileId=sh_price, body=newfile).execute()
        new_price_id = new_price['id']
        driveService.permissions().create(
            fileId=new_price_id,
            body={'type': 'user', 'role': 'writer',
                  'emailAddress': 'princealexxx.623@gmail.com'},
            fields='id'
        ).execute()

        Files.objects.create(sheet_id=new_price_id, type_file=object,
                             product=Product.objects.get(pk=pk))

    elif object == 'zam':
        folder = '1-5Qscphr4n_hGPGGnLFkO84LD2pjicP0'
        file_metadata = {
            'name': f'Замер ({datetime.now().date()}): {str(cust)} - {str(prod)}',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [folder]
        }
        new_folder = driveService.files().create(body=file_metadata, fields='id').execute()
        folder_id = new_folder['id']
        driveService.permissions().create(
            fileId=folder_id,
            body={'type': 'user', 'role': 'writer',
                  'emailAddress': 'princealexxx.623@gmail.com'},
            fields='id'
        ).execute()

        Files.objects.create(sheet_id=folder_id, type_file=object,
                             product=Product.objects.get(pk=pk))

    elif object == 'pr':
        folder = '1-5Qscphr4n_hGPGGnLFkO84LD2pjicP0'
        file_metadata = {
            'name': f'Проект ({datetime.now().date()}): {str(cust)} - {str(prod)}',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [folder]
        }
        new_folder = driveService.files().create(body=file_metadata, fields='id').execute()
        folder_id = new_folder['id']
        driveService.permissions().create(
            fileId=folder_id,
            body={'type': 'user', 'role': 'writer',
                  'emailAddress': 'princealexxx.623@gmail.com'},
            fields='id'
        ).execute()

        Files.objects.create(sheet_id=folder_id, type_file=object,
                             product=Product.objects.get(pk=pk))


    print([i for i in str(cust)])

    return render(request, 'crm/includes/crm_product_files.html',
                  {'files': Files.objects.filter(product_id=pk)})
