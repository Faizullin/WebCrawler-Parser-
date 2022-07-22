from django.core.mail import send_mail
import time


def send_email(user_mail):
	print('Тест',"Это тест",user_mail)
	time.sleep(1000)
	print("end")

def get_error(Object,*args,**kwargs):
	try:
		ob=Object.objects.get(*args,**kwargs)
		return ob
	except:#Object.DoesNotExist
		return None
	else:
		return None