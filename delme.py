import openpyxl as op
from googletrans import Translator
import time

def tr(text):
    s1=time.time()
    splited_text=text.split('.')
    ll=0
    dividor_length=3000
    tt=[]
    index = 0
    result=""
    for i in range(len(splited_text)):
        ll+= (len(splited_text[i])+1)
        if ll> dividor_length:
            ll-= len(splited_text[i])-1
            print("big divide",ll)
            
            result +=translator.translate('.'.join(tt), dest='zh-cn').text
            tt.clear()
            ll= len(splited_text[i])
            if len(splited_text[i])>dividor_length:
                print("ERROR: too big sentence -",len(splited_text[i]))
                return False,None
            tt.append(splited_text[i])
        else:
            tt.append(splited_text[i])
        #print(len(splited_text[i]))
    if tt:
        result+=translator.translate('.'.join(tt), dest='zh-cn').text
    s2=time.time()

    print(s2-s1)
    return True,result

translator = Translator()
wb =op.load_workbook('media\\crawler\\File1_10.xlsx')

ws = wb['Kazakh']
data=ws['A1'].value

st,res = tr(data)
wb['Chinese']['A1'].value = res
wb.save('media\\crawler\\File1_10.xlsx')
wb.close()
print(res)
