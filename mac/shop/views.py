from django.shortcuts import render
from .models import Product, Contact, Orders, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum
from shop.forms import  NewUserForm,LoginUserForm,OneTimePasswordForm
from django.db.models import Q
from django.contrib.sessions.models import Session
from shop import models
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import pymsgbox
import win10toast
from win10toast import ToastNotifier
import time
import re
# Create your views here.
from django.http import HttpResponse,HttpResponseRedirect
MERCHANT_KEY = 'Xyz'
#############################################################
def LogOut(request):
    del request.session['is_logged']
    return HttpResponseRedirect('../loginPage')
#got to register page
def regPage(request):
    if request.session.has_key('is_logged'):
        return HttpResponseRedirect("../")
    form=NewUserForm()
    res=render(request,'shop/signup.html',{'form':form})
    return res
#registration of user
def adduser(request):
    if request.method=="POST":
        #form=NewUserForm(request.POST)
        reg=models.Register.objects.filter(email=request.POST['email'])
        n=ToastNotifier()
        if len(reg)!=0:
            res=render(request,'shop/signup.html',{'msg': n.show_toast("Register","You Have Already Registered with This Account",duration=2,icon_path="shop/adduser/")})
            return res
        else:
            try:
                #movile no validation
                Pattern = re.compile("(0/91)?[7-9][0-9]{9}")
                s = str(request.POST['mobile'])
                if Pattern.match(s):
                    n=ToastNotifier()
                    print("valid")
                else:
                    n=ToastNotifier()
                    n.show_toast("Mobile no","Invalid mobile no",duration=2,icon_path="shop/adduser/")
                    raise SyntaxError("invalid mobile no")
                #send registration mail to user
                sender_email="xyz@gmail.com"
                password="xyz"
                rec_email=request.POST['email']
                body="You Have Successfully Registered on E-marketPlace"
                subject = 'Registration'
                message = MIMEMultipart()
                message['sender_email']=sender_email
                message['rec_email']=rec_email
                message['subject']=subject
                message.attach(MIMEText(body, 'plain'))
                text = message.as_string()
                mail = smtplib.SMTP('smtp.gmail.com', 587)
                mail.ehlo()
                mail.starttls()
                mail.login(sender_email,password)
                print("login successful")
                mail.sendmail(sender_email,rec_email, text)
                print("email has been sent")

                reg=models.Register()#create object of register table(model)
                reg.username=request.POST['username']#get username from html form
                reg.email=request.POST['email']#get email from html form
                reg.password=request.POST['password']#get password from html form
                reg.mobile=request.POST['mobile']#get mobile no from html form
                reg.save()
            except SyntaxError:
                return HttpResponseRedirect('../register')
            except:
                n=ToastNotifier()
                n.show_toast("Registration","oops! Something went Wrong! Check Your Internet Connection",duration=2,icon_path="shop/adduser/")
                return HttpResponseRedirect('../register')
            n=ToastNotifier()
            n.show_toast("Register","You Have Successfully Registered on E-MarketPlace",duration=2,icon_path="shop/adduser/")
            return HttpResponseRedirect('../loginPage')
    else:
        s1="not reg"
        return HttpResponse(s1)
#go to login page
def loginPage(request):
    if request.session.has_key('is_logged'):
        return HttpResponseRedirect("../")
    #form=LoginUserForm()
    res=render(request,'shop/signin.html')
    return res
#otp send function
def fun_otp_send(request):
    sender_email="xyz@gmail.com"
    password="xyz"
    rec_email=request.session['user_email']
    l=['1','2','3','a','b','c','4','d','e','f','5','g','h','i','j','6','k','l','m','n','7','o','p','q','8','r','s','t','u','v','9','w','x','y','z']
    random.shuffle(l)
    l1=l[0:6]
    body=""
    for i in l1:
	       body=body+i
    subject = 'One Time Password'
    message = MIMEMultipart()
    message['sender_email']=sender_email
    message['rec_email']=rec_email
    message['subject']=subject
    message.attach(MIMEText(body, 'plain'))
    text = message.as_string()
    request.session['msg_otp']=body
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login(sender_email,password)
    print("login successful")
    mail.sendmail(sender_email,rec_email, text)
    print("email has been sent")
    form2=OneTimePasswordForm()
    n=ToastNotifier()
    res=render(request,"shop/onetime.html",{'form2':form2,'msg': n.show_toast("OTP","OTP is sent to Your Registered Gmail Account",duration=2,icon_path="shop/adduser/")})
    return res
#user login
def success(request):
    if request.method=="POST":
        #form=LoginUserForm(request.POST)
        reg=models.Register.objects.filter(Q(email=request.POST['email']) & Q (password=request.POST['password']))
        if len(reg)==1:
            for i in reg:
                global user
                user=i.username
                variable=i.id
                user=user.split()
            request.session['id']=variable
            request.session['username']=user[0].capitalize()
            form2=OneTimePasswordForm()
            res=render(request,"shop/onetime.html",{'form2':form2})
            rec_email=request.POST['email']
            request.session['user_email']=rec_email
            #email sending logic for otp
            try:
                fun_otp_send(request)
            except:
                n=ToastNotifier()
                res=render(request,'shop/signin.html',{'msg': n.show_toast("OTP","oops! Something went Wrong! Check Your Internet Connection",duration=2,icon_path="shop/adduser/")})
                return res
            res=render(request,'shop/onetime.html',{'form2':form2})
            return res
        else:
            n=ToastNotifier()
            res=render(request,'shop/signin.html',{'form':form,'msg': n.show_toast("Login","Invalid Email or Password",duration=2,icon_path="shop/adduser/")})
            return res
def OTPPage(request):
    if request.method=='POST':

        form=OneTimePasswordForm(request.POST)
        if form.data['otp']==request.session['msg_otp'] and form.data['otp']!="0":
            request.session['is_logged']=True
            request.session['msg_otp']="0"
            print(request.session['msg_otp'])
            return HttpResponseRedirect('/shop/')
        else:
            return HttpResponse("not valid")
#go to user profile
def profile(request):
    if request.session.has_key('is_logged'):
        reg=models.Register.objects.get(id=request.session['id'])
        fields={'username':reg.username,'mobile':reg.mobile,'email':reg.email}
        form=NewUserForm(initial=fields)
        res=render(request,'shop/user_profile.html',{'form':form,'reg':reg})
        print("profile id is: ",request.session['id'])
        return res
    else:
        return HttpResponseRedirect("../loginPage")
#update profile
def updatePro(request):
    if request.method=="POST":
        form=NewUserForm(request.POST)
        res=models.Register()
        res.id=request.POST['cid']
        res.password=request.POST['password']
        res.username=form.data['username']
        res.email=form.data['email']
        res.mobile=form.data['mobile']
        res.save()
        uname=res.username.split()
        request.session['username']=uname[0].capitalize()
        print("username is: ",request.session['username'])
        return HttpResponseRedirect("../profile/")

#####################################################################################################
def index(request):
    if request.session.has_key('is_logged'):
        allProds = []
        catprods = Product.objects.values('category', 'id')
        cats = {item['category'] for item in catprods}
        for cat in cats:
            prod = Product.objects.filter(category=cat)
            n = len(prod)
            nSlides = n // 4 + ceil((n / 4) - (n // 4))
            allProds.append([prod, range(1, nSlides), nSlides])
        params = {'allProds':allProds}
        return render(request, 'shop/index.html', params)
    else:
        return HttpResponseRedirect("shop/loginPage")


def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)


def about(request):
    if request.session.has_key('is_logged'):
        return render(request, 'shop/about.html')
    else:
        return HttpResponseRedirect("../loginPage")


def contact(request):
    if request.session.has_key('is_logged'):
        thank = False
        if request.method=="POST":
            name = request.POST.get('name', '')
            email = request.POST.get('email', '')
            phone = request.POST.get('phone', '')
            desc = request.POST.get('desc', '')
            contact = Contact(name=name, email=email, phone=phone, desc=desc)
            contact.save()
            thank = True
        return render(request, 'shop/contact.html', {'thank': thank})
    else:
        return HttpResponseRedirect("../loginPage")




def productView(request, myid):
    if request.session.has_key('is_logged'):
        # Fetch the product using the id
        product = Product.objects.filter(id=myid)
        return render(request, 'shop/prodView.html', {'product':product[0]})
    else:
        return HttpResponseRedirect("../loginPage")


def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        # return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
        # Request paytm to transfer the amount to your account after payment by user
        param_dict = {

                'MID': 'xyz',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'shop/paytm.html', {'param_dict': param_dict})

    return render(request, 'shop/checkout.html')


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})
