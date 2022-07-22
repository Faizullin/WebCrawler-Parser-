import os,openpyxl, requests, docx,openpyxl,time
import httpx
#from sys import getsizeof as gs

from bs4 import BeautifulSoup
from googletrans import Translator
from urllib.parse import urlparse,urljoin
from background_task import background
from background_task.models import Task,CompletedTask
from .service import send_email,get_error
from django.conf import settings
from .models import SearchedLink


# def send_spam_email(user_email):
# 	send_email(user_email)

# @background(schedule=1)
# def start_search(user_id):
# 	print(user_id)	
# 	with open("t.text","a+") as f:
# 		f.write(str(time.time())+str(user_id)+"\n")





media_folder = os.path.join(settings.MEDIA_ROOT,"crawler")
file_type_choices={'xlsx':'xlsx','doc':'docx','txt':'txt'}
file_number_choices = (10,50,100)
def get_status(user_id):
	return Task.objects.filter(creator_object_id=user_id),CompletedTask.objects.filter(creator_object_id=user_id)


def get_filepath(object_id=None,file_number=None,file_type=None):
	
	print(object_id,file_number,file_type)
	file_number=int(file_number)
	if (file_number in file_number_choices) and (file_type in file_type_choices.keys() ) and file_number:
		ending = file_type_choices[file_type]
		return os.path.join(media_folder,f'File{object_id}_{file_number}.{ending}')

	raise Exception("Error input filename data")

class TextTranslator:
	

	def __init__(self):
		self.translator = Translator(timeout  = httpx.Timeout(8))
		self.dividor_length=3000
	def translate(self,text,dest_language = 'zh-cn'):
		result = ""
		text = text[0] + '. \n'+text[1]
		if len(text)>self.dividor_length:
			print("BIG text")
			splited_text=text.split('.')
			n=len(splited_text)
			ll=0
			tt=[]
			for i in range(n):
				ll+= (len(splited_text[i])+1)
				if ll> self.dividor_length:
					ll-= len(splited_text[i])-1

					result +=self.translator.translate('.'.join(tt), dest='zh-cn').text
					#print("-----> translate ",tt,len('.'.join()),"into ",self.translator.translate('.'.join(tt), dest='zh-cn').text)
					tt.clear()
					ll = len(splited_text[i])

					if ll > self.dividor_length:
						print("ERROR: too big sentence -",ll)
						return False,None
					tt.append(splited_text[i])
				else:
					tt.append(splited_text[i])
			if tt:
			    result+=self.translator.translate('.'.join(tt), dest='zh-cn').text

		else:
			result = self.translator.translate(text, dest=dest_language).text
			#print(result)
		index = result.find('\n')
		if index!=-1:
			return True,(result[:index],result[index+1:])
		return False,None

		
class TxtDocument:
	buffer=''
	def __init__(self,file=None):
		ob = open(file,'w+', encoding='utf-8')
		ob.close()
	def add(self,url,content,ending=True):
		self.buffer = self.buffer + content + '\n'+url + '\n'
		if ending:
			self.buffer+='_____________________________________\n'
		else:
			self.buffer+='\n'
	def save(self,file=None):
		with open(file,'a+', encoding='utf-8') as f:
			f.write(self.buffer)
		self.buffer = ''
	# def close(self):
	# 	self.object.close()

class MyFilesClass:
	
	def __init__(self,object_id=None,file_number=None):
		self.document = {}
		self.files={}
		for key_type in file_type_choices.keys():
			self.files[key_type]=get_filepath(object_id = object_id,file_type=key_type,file_number=file_number)
		self.object_id = object_id
		print(self.files);self.xl=1
	def create(self):
		self.document['xlsx']=openpyxl.Workbook()
		self.document['doc']=docx.Document()
		self.document['txt'] = TxtDocument(self.files['txt'])
		for f in self.files.keys():
			if os.path.exists(self.files[f]):
				os.remove(self.files[f])
		self.document['xlsx'].remove(self.document['xlsx'].active)
		self.worksheet1 =self.document['xlsx'].create_sheet("Kazakh", 0)
		self.worksheet2 =self.document['xlsx'].create_sheet("Chinese",1)
		self.worksheet1.column_dimensions['A'].width=160
		self.worksheet1.column_dimensions['B'].width=120
		self.worksheet2.column_dimensions['A'].width=160
		self.worksheet2.column_dimensions['B'].width=120
		
		self.save()#<-min number
		#self.save()


	def add(self,n:int,content_url:list,orig_content:list,translated_content:list,auto_save=False):
		print("ADD:",n);
		if n==0:
			return;
		for i in range(0,n):
			translated = '\n'.join(translated_content[i])
			original = '\n'.join(orig_content[i])
			self.worksheet1.append([original,content_url[i]])
			self.worksheet1["A"+str(self.xl)].alignment = openpyxl.styles.Alignment(wrap_text=True)
			self.worksheet2.append([translated,content_url[i]])
			self.worksheet2["A"+str(self.xl)].alignment = openpyxl.styles.Alignment(wrap_text=True)

			self.document['doc'].add_heading(orig_content[i][0])
			self.document['doc'].add_paragraph(orig_content[i][1])
			self.document['doc'].add_paragraph(content_url[i])
			self.document['doc'].add_heading(translated_content[i][0])
			self.document['doc'].add_paragraph(translated_content[i][1])
			self.document['doc'].add_paragraph(content_url[i])

			self.document['txt'].add(content_url[i],original,ending=False)
			self.document['txt'].add(content_url[i],translated,ending=True);self.xl+=1

		if auto_save:
			self.save()
	def remove(self):
		self.document['xlsx'].remove(self.worksheet1)
		self.document['xlsx'].remove(self.worksheet2)
		for key in self.files.keys():
			if os.path.exists(self.files[key]):
				os.remove(self.files[key]) 

	def save(self):
		print("save")
		for key in self.files.keys():
			self.document[key].save(self.files[key])



max_number_of_iterate=150
errors=[]
iterate_add_number = 30

def process_article_data(article_data):
	for key in article_data.keys():
		if (not '.' in article_data[key]) and ('#' not in article_data[key]):
			article_data[key]='.'+article_data[key]
	if len(article_data['article_news_body'].split() )>1:
		article_data['article_news_body']=article_data['article_news_body'].split()
	else:
		article_data['article_news_body']=[article_data['article_news_body'],'p']
	return article_data
def save_error(obj,text):
	if not obj:
		raise Exception("Not found by requested_url by id")
	obj.has_error=True;
	obj.error_body=str(text)
	obj.is_ready = True
	obj.save()
@background(schedule=1)
def search(requested_url=None,object_id=None,main_domain=None,article_data=None):
	print("START WORK")
	main_domain = requested_url
	st,res_raw_links = link_gathering(requested_url,main_domain)
	if not st and res_raw_links:
		save_error(get_error(SearchedLink,id=object_id),res_raw_links)
		return;

	article_data = process_article_data(article_data)
	print(article_data)
	length_of_res_links = len(res_raw_links)
	if length_of_res_links > max_number_of_iterate:
		length_of_res_links=max_number_of_iterate
	print("RES_LINK:",length_of_res_links)
	documents = []
	a = sorted(file_number_choices,reverse=True)
	for i in range(len(a)):
		documents.append( MyFilesClass(object_id=object_id,file_number=a[i]) )
		documents[i].create()
	print(documents[0].files)
	del a;
	index = 0
	success_number=0
	old_success_number=0
	s1=time.time()
	translator = TextTranslator()
	for required_number in file_number_choices:
		file_number = required_number#30,50,100
		if file_number>length_of_res_links:
			file_number = length_of_res_links
		if success_number>=file_number:
			break
		content_url=[]
		orig_content=[]
		translated_content=[]
		print("LOOK at",required_number,"->",file_number)
		while((file_number!= success_number) and (index<length_of_res_links)):
			st,res_raw_content = content_gathering(res_raw_links[index],article_data)
			print(index,")",res_raw_links[index],st)
			if st:
				st,tt = translator.translate(res_raw_content)
				print("TRANSLATE",st)
				if st:
					orig_content.append(res_raw_content)
					translated_content.append(tt)
					content_url.append(res_raw_links[index])

				success_number+=1
			index+=1
			if success_number%iterate_add_number==0:
				if success_number!=old_success_number:
					old_success_number = success_number
					print("Iterate at",index,"(",success_number,")")
					st,tt = translator.translate(res_raw_content)
					for i in range(len(documents)):
						documents[i].add(len(content_url),content_url,orig_content,translated_content,auto_save=True)
					content_url.clear()
					orig_content.clear()
					translated_content.clear()
		if success_number==0:
			continue
		for i in range(len(documents)):
			print("simple save to",i,' ',required_number,"(",success_number,")")
			documents[i].add(len(content_url),content_url,orig_content,translated_content,auto_save=True) 
		documents.pop()
	s2=time.time()
	print("COMPLETED AT ",s2-s1,"s")
	item_ = get_error(SearchedLink,id=object_id)

	if not item_:

		raise Exception("Not found by requested_url by id")
	item_.is_ready = True
	if success_number == 0:
		save_error(item_,"Информация не найдена")
		return;
	article_data['article_news_body'] = ' '.join(article_data['article_news_body'])
	for key,val in article_data.items():
		item_.__dict__[key]=val;
	item_.save()


def link_gathering(a,main_domain):
    basa = []
    try:
        response = requests.get(a,timeout = 3)
        if response.status_code!=200:
            return False,"Ошибка на странице"
    except:
         return False,'Страница не найдена'
    soup=BeautifulSoup(response.content, 'lxml')
    del response
    errors=[]
    for i in soup.find_all("a"):
        href_object =i.get('href')
        #print(i,href_object,bool(href_object),'\n-------')
        if (not href_object) or ('img' in href_object) or ('image' in href_object) or ('#' in href_object):
            continue
        if href_object.startswith('http'):
            this_domain=None
            try:
                this_domain = urlparse(href_object)
                this_domain = this_domain.scheme+"://"+this_domain.hostname+this_domain.path
                
            except Exception as err:
                errors.append(href_object)
                continue
            if not (this_domain.startswith(main_domain)):
                errors.append(this_domain)
                continue
            basa.append(this_domain)
        elif href_object.startswith('/'):
            basa.append(urljoin(main_domain, href_object))
        else:
        	errors.append(href_object)
    print(basa,len(basa),len(soup.find_all("a")))
    print("ERRORS:",errors)
    basa=list(set(basa))
    if len(basa)<2:
    	return False,'Информация не найдена'
    return True,basa

def content_gathering(link,article_data):
	response=None
	try:
		response = requests.get(link)
		if response.status_code!=200:
			print("DONT WORK"+link)
			return False,None
	except:
		print("DONT WORK"+link)
		return False,None
	soup = BeautifulSoup(response.content, 'lxml')
	try:
		div_block_object=soup.select_one(article_data["article_news_block"])
		if (not div_block_object):
			print("NO ARTCILE BLOCK"+link)
			return False,None
		div_title_object=soup.select_one(article_data["article_news_title"])#news_block
		#print("SELECT",div_title_object)
		if not div_title_object:
			print("NO ARTCILE TITLE "+article_data["article_news_title"]+link)
			return False,None
		content_title = div_title_object.get_text()
		div_body_objects=soup.select_one(article_data["article_news_body"][0])#news_block
		content_body=''
		for k in div_body_objects.find_all(article_data["article_news_body"][-1]):
			content_body+=k.get_text()
		return True,(content_title,content_body)
	except Exception as err:
		print('Error',err)
		return False,str(err)
