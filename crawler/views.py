import os

from django.conf import settings
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator

from django.urls import path,reverse_lazy,reverse
from django.http import HttpResponse,JsonResponse

from django.views.generic import TemplateView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from background_task.models import CompletedTask,Task
from . import tasks
from .service import get_error
from .models import SearchedLink
from .forms import SearchedLinkForm, RegisterUserForm,LoginUserForm, DownloadForm
from . import views


file_content_types={
    'xlsx':"vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "doc":'vnd.openxmlformats-officedocument.wordprocessingml.document',
    'txt':'force-download'
}

class HeaderMixin(object):
     def check_auth(self,context={}):
        if not self.request.user.is_authenticated:
            context['form_login']=LoginUserForm()
            return False
        return True
class CrawlerIndex(HeaderMixin,TemplateView):
    template_name = 'crawler/index.html'
    def get_context_data(self, **kwargs):
        context = super(TemplateView,self).get_context_data(**kwargs)
        print(self.request.session.get('requested_object_id'))
        context.update({
            'form_search': SearchedLinkForm(),
            'form_download' : DownloadForm()
        })
        self.check_auth(context)
        print("CONTECT",context)
        return context




def Download(request):

    if request.method=='GET':
        return redirect("home")
    #print(request.POST)
    if not request.user.is_authenticated:
        return JsonResponse({'msg':"Пожалуйста авторезуйтесь"},status=401)
    downloadform = DownloadForm(request.POST)
    if not downloadform.is_valid():
        #print(downloadform.errors)
        return JsonResponse({'msg':"Ошибка валидации"},status=403)
    requested_object_id = request.session.get('requested_object_id')
    print(requested_object_id,downloadform.cleaned_data)
    if requested_object_id!=None:
        item_ = get_error(SearchedLink,id=requested_object_id)
        print(item_)
        if item_:
            # request.session['requested_object_id']=item_.pk
            # request.session.modified = True
            print("session:",request.session.get('requested_object_id'))
            if not item_.is_ready:
                return JsonResponse({'msg':"Идет поиск и сборка информации...",'success':False},status=200)
            if item_.has_error:
                return JsonResponse({'msg':"Ошибка во время запроса {}:\n{}".format(item_.url,item_.error_body),'success':False},status=500)
            file_number = downloadform.cleaned_data.get('file_number',None)
            file_type = downloadform.cleaned_data.get('file_type',None)
            if not (file_type and file_number):
                return JsonResponse({'msg':"Ошибка валидации(Недостаточно данных ввода)",'success':False},status=500)
            file_path = tasks.get_filepath(object_id=requested_object_id,file_number=file_number,file_type=file_type)
            if not os.path.exists(file_path):
                return JsonResponse({'msg':"Не смог найти файл",'success':False},status=500)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                print("AJAX request")
                return JsonResponse({'success':True,'msg':''},status=200)
            response=None

            with open(file_path,'rb') as f:
                file_content = f.read()
                response = HttpResponse(
                    file_content,content_type='application/'+file_content_types[file_type]
                )
                response['Content-Length'] = len(file_content)
            response['success']=True
            response['Content-Disposition'] = 'attachment; filename=file.'+file_type
            return response
    return JsonResponse({'msg':"С начало Введите url страницы в поиске"},status=200)
article_data__=['article_news_block','article_news_body','article_news_title']
def CrawlerSearch(request):
    if not request.user.is_authenticated:
        return JsonResponse({'msg':"Пожалуйста авторезуйтесь","success":False},status=500)
    urlg=SearchedLinkForm(request.POST)
    print(request.POST,request.session.get('requested_object_id'))
    if urlg.is_valid():
        print(urlg.cleaned_data)
        requested_url= urlg.cleaned_data['url']
        if requested_url.endswith('/'):
            requested_url=requested_url[:-1]
        print("requested url:",requested_url)
        cond={'url':requested_url}
        for key in article_data__:
            cond[key] = urlg.cleaned_data.get(key,'')

        print("search condtions:",cond)
        items = SearchedLink.objects.filter(**cond)      

        if not items:
            item_ = urlg.save(commit=False)
            item_.creator_id = request.user
            item_.save()
            article_data = {}
            for key in article_data__:
                article_data[key]=urlg.cleaned_data.get(key)
            tasks.search(article_data=article_data,requested_url=requested_url,object_id = item_.pk,schedule=1,verbose_name="CrawlerSearch", creator=request.user)
            request.session['requested_object_id'] = item_.pk
            request.session.modified = True
            return JsonResponse({'success':True,'msg':"Начало поиска и сборки информации\nПодождите несколько секунд..."},status=200)
        
       
        item_=None
        print(items)
        try:
            item_ = items.get()
        except Exception as err:
            return JsonResponse({'success':False,'msg':f"Ошибка на сервере (БД {err})"},status=500)
        request.session['requested_object_id'] = item_.pk
        request.session.modified = True
        print("Session:",request.session.get('requested_object_id'))
        if not item_.is_ready:
            return JsonResponse({'success':True,'msg':"Идет поиск и сборка информации..."},status=200)
        if item_.has_error:
            return JsonResponse({'success':False,'msg':"Ошибка во время запроса {}:\n{}".format(item_.url,item_.error_body)},status=500)
        return JsonResponse({'success':True,'msg':"Поиск завершен"},status=200)
    return JsonResponse({'success':False,'msg':"Ошибка валидации"},status=500)

def CrawlerLogin(request):
    if request.method=='POST':
        print(request.POST)
        urlg = LoginUserForm(request,request.POST)

        if urlg.is_valid():

            login(request, urlg.get_user())
            return JsonResponse({"success":True,'msg':'Вы успешно авторизовались','action':"reload"},status=200)
        return JsonResponse({"success":False,'response':urlg.errors,'action':"html"},status=403)
    else:
        urlg = AuthenticationForm(request)
    context={
        'form_search':SearchedLinkForm(),
        'form_login':urlg,
        'form_download' : DownloadForm()
    }
    return render(request,'crawler/index.html',context)



def CrawlerRegister(request):
    if request.method=='POST':
        urlg = RegisterUserForm(request.POST)
        if urlg.is_valid():
            user = urlg.save()
            login(request,user)
            return JsonResponse({"success":True,'msg':'Вы успешно зарегестрировались','action':"reload"},status=200)
        return JsonResponse({"success":False,'response':urlg.errors,'action':"html"},status=403)
    else:
        urlg = RegisterUserForm()
    context={
        'form_register':urlg,
        'form_search':SearchedLinkForm(),
        'form_download' : DownloadForm()

    }
    return render(request,'crawler/index.html',context)


def CrawlerLogout(request):
    logout(request)
    if request.META.get('HTTP_REFERER'):
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect(reverse('login')+'#login')



class CrawlerUrlsList(HeaderMixin,TemplateView):
    template_name = 'crawler/urls_list.html'

    def get_context_data(self, **kwargs):
        print(reverse('login'))
        context = super(CrawlerUrlsList,self).get_context_data(**kwargs)
        current_tasks=[]
        if self.check_auth(context):
            not_ready_items = SearchedLink.objects.filter(creator_id=self.request.user,is_ready=False)
            current_tasks = [i for i in not_ready_items if Task.objects.filter(creator_object_id=i.creator_id.id)]
        context.update({
            'current_tasks': current_tasks,
            'completed_tasks': SearchedLink.objects.filter(is_ready=True),
            'title':'DB'
        })

        print(context)
        return context
