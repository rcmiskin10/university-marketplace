from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render_to_response, RequestContext, Http404, HttpResponseRedirect, render, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django import forms
import os
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import modelformset_factory
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib import messages
import hashlib, datetime, random
import json
import urllib, json, boto3
from accounts.forms import RegistrationForm
from accounts.models import MyUser, UserProfile, Rating
from .forms import LoginForm
from products.models import Product, Category, DoService, WantService, ServiceType, WantServiceType
from products.forms import ProductForm, DoServiceForm, WantServiceForm, EditProductForm
from courses.forms import CourseForm
from courses.models import Course
from direct_message.forms import ComposeForm
from direct_message.models import DirectMessage, Convo
from local.models import Place, LocalRating, PlaceCategory
from accounts.models import University, UserPicture, Contact
from accounts.forms import UserPictureForm, ContactForm

from PIL import Image, ExifTags

def contact(request):
    contact_form = ContactForm(request.POST or None)
    if contact_form.is_valid():
        
        email = contact_form.cleaned_data['email']
        name = contact_form.cleaned_data['name']
        phone = contact_form.cleaned_data['phone']
        body = contact_form.cleaned_data['body']
        
        new_contact = Contact()
        new_contact.email = email
        new_contact.name = name
        new_contact.phone = phone
        new_contact.body = body

        new_contact.save()
        sg_email = 'info@studentgrounds.org'
        # Send email 
        email_subject = 'Landing Page Message'
        email_body = "%s <br> %s <br> %s <br> %s <br>" % (name, email, phone, body)

        send_mail(email_subject, email_body, 'studentgroundsinc@gmail.com',
            [sg_email], fail_silently=False)
        response_data = {}

        response_data['success'] = 'True'
        
        new_data = json.dumps(response_data)

        return HttpResponse(new_data, content_type='application/json')
        
    else:
        response_data = {}
        
        response_data['errors'] = contact_form.errors.as_json()
        response_data['success'] = 'False'
        new_data = json.dumps(response_data)

        return HttpResponse(new_data, content_type='application/json') 

def terms(request):

    return render_to_response('terms.html', locals(), context_instance=RequestContext(request))

def privacy(request):

    return render_to_response('privacy.html', locals(), context_instance=RequestContext(request))

def email_search(request):
    if request.method == 'POST':
            search_text = request.POST['search_text']
            

            if '.edu' in search_text:   
                try:
                    domain = search_text.split("@")[-1]
                    

                    university = University.objects.filter(domain=domain)

                    school = university
                except University.DoesNotExist:
                    try:
                        test = domain.count('.')
                        domain = domain.split('.')[test-1] +"."+ domain.split('.')[test]

                        university = University.objects.get(domain=domain)
                        school = university
                    except:
                        school = "Sorry. We could not find your school."
                        
               
                    
                    


    return render_to_response('email-search.html', locals(), context_instance=RequestContext(request))
def registration(request):
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        site = request.META['HTTP_HOST']
        email = form.cleaned_data['email']
        username = form.cleaned_data['username']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        password = form.cleaned_data['password2']
        referral = form.cleaned_data['referral']

        domain = email.split("@")[-1]
        university = University.objects.get(domain=domain)
        print university
        new_user = MyUser()
        new_user.email = email
        new_user.username = username
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.referral = referral
        new_user.set_password(password)
        if university is not None:
            new_user.university = university
        new_user.save()

        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]            
        activation_key = hashlib.sha1(salt+email).hexdigest()            
        key_expires = datetime.datetime.today() + datetime.timedelta(2)

        #Get user by username
        user=MyUser.objects.get(email=email)

        # Create and save user profile                                                                                                                                  
        new_profile = UserProfile(user=user, activation_key=activation_key, 
            key_expires=key_expires)
        new_profile.save()
        email = form.cleaned_data['email']
        # Send email with activation key
        email_subject = 'Account confirmation'
        email_body = "Hey %s, thanks for signing up. To activate your account, click this link within \
        48hours http://%s/accounts/confirm/%s" % (email, site, activation_key)

        send_mail(email_subject, email_body, 'studentgroundsinc@gmail.com',
            [email], fail_silently=False)
        response_data = {}

        response_data['success'] = True
        response_data['url'] = '/registration_complete/'
        new_data = json.dumps(response_data)

        return HttpResponse(new_data, content_type='application/json')
        
    else:
        response_data = {}
        
        response_data['errors'] = form.errors.as_json()
        response_data['success'] = False
        new_data = json.dumps(response_data)

        return HttpResponse(new_data, content_type='application/json')  
def home(request):
    if not request.user.is_authenticated():
        login_form = LoginForm(request.POST or None)
        form = RegistrationForm(request.POST or None)
        contact_form = ContactForm(request.POST or None) 
        
        return render_to_response('home.html', locals(), context_instance=RequestContext(request))

    else:
        uni = request.user.university.id
        return HttpResponseRedirect(reverse('main', args=(uni,)))


def main(request, id):
    if request.user.is_authenticated():
        try:
            school = University.objects.get(id=id)
        except:
            uni = request.user.university.id
            return HttpResponseRedirect(reverse('main', args=(uni,)))

        if request.user.university == school:
            

            products = Product.objects.filter(university=school).filter(sold=False).order_by("-timestamp").exclude(owner=request.user)

            school = University.objects.get(id=id)
            
            newest = Product.objects.filter(university=school).filter(sold=False).order_by('-timestamp').exclude(owner=request.user)
            user_compose_form = ComposeForm(request.POST or None)
            courses = Course.objects.filter(user=request.user)
            
            product_form = ProductForm(request.POST or None, request.FILES or None, prefix='product')

            received_messages = DirectMessage.objects.filter(receiver=request.user).filter(read=False)
            sent_messages = DirectMessage.objects.filter(sender=request.user).filter(read=False)
            sender_list = []
            id_list = []
            for item in sent_messages:
                if not item.receiver.id in id_list:
                    sender_list.append(item.receiver.first_name +" "+ item.receiver.last_name)
                    id_list.append(item.receiver.id)

            for item in received_messages:
                if not item.sender.id in id_list:
                    sender_list.append(item.sender.first_name +" "+ item.sender.last_name)
                    id_list.append(item.sender.id)
            send_id_list = zip(sender_list, id_list)


            return render_to_response('main.html', locals(), context_instance=RequestContext(request))
        
        else:
            uni = request.user.university.id
            return HttpResponseRedirect(reverse('main', args=(uni,)))
    else:
        return HttpResponseRedirect('/login/')
def my_profile(request, id, profid):
    if request.user.is_authenticated():
        try:
            user = MyUser.objects.get(id=profid)
            school = University.objects.get(id=id)
        except:
            uni = request.user.university.id
            user_id = request.user.id
            return HttpResponseRedirect(reverse('my_profile', args=(uni,user_id)))
        if user.id == request.user.id and school.id == request.user.university.id:
            
            picture = UserPicture.objects.filter(user=user)
            UserPictureFormset = modelformset_factory(UserPicture, form=UserPictureForm, extra=1, max_num=1)
            formset_pic = UserPictureFormset(request.POST or None, request.FILES or None, queryset=picture)
            all_products = Product.objects.filter(owner=user).filter(university=school)
            rating = Rating.objects.filter(profile=user)
            count = Rating.objects.filter(profile=user).count()
            rating_list = []
            if rating:
                for item in rating:
                    rating_list.append(item.number)
                number = sum(rating_list)/float(count)
                rounded_num = round(number * 2.0) / 2.0
            else:
                rounded_num = 0
            user_list = []

            for item in rating:
                user_list.append(item.rater)
            if request.user in user_list:
                rated = 1   

            else:
                rated = 0
            return render_to_response('user_profile/my_profile.html', locals(), context_instance=RequestContext(request))
        else:
            uni = request.user.university.id
            user_id = request.user.id
            return HttpResponseRedirect(reverse('my_profile', args=(uni,user_id)))
    else:
        return HttpResponseRedirect('/login/')

def my_profile_selling(request, id, profid):
    if request.user.is_authenticated():
        try:
            user = MyUser.objects.get(id=profid)
            school = University.objects.get(id=id)
        except:
            uni = request.user.university.id
            user_id = request.user.id
            return HttpResponseRedirect(reverse('my_profile_selling', args=(uni,user_id)))
        if user.id == request.user.id and school.id == request.user.university.id:
            
            picture = UserPicture.objects.filter(user=user)
            UserPictureFormset = modelformset_factory(UserPicture, form=UserPictureForm, extra=1, max_num=1)
            formset_pic = UserPictureFormset(request.POST or None, request.FILES or None, queryset=picture)
            selling_products = Product.objects.filter(owner=user).filter(university=school).filter(sold=False)
            rating = Rating.objects.filter(profile=user)
            count = Rating.objects.filter(profile=user).count()
            rating_list = []
            if rating:
                for item in rating:
                    rating_list.append(item.number)
                number = sum(rating_list)/float(count)
                rounded_num = round(number * 2.0) / 2.0
            else:
                rounded_num = 0
            user_list = []

            for item in rating:
                user_list.append(item.rater)
            if request.user in user_list:
                rated = 1   

            else:
                rated = 0
            return render_to_response('user_profile/selling_profile.html', locals(), context_instance=RequestContext(request))
        else:
            uni = request.user.university.id
            user_id = request.user.id
            return HttpResponseRedirect(reverse('my_profile_selling', args=(uni,user_id)))
    else:
        return HttpResponseRedirect('/login/')

def my_profile_sold(request, id, profid):
    if request.user.is_authenticated():
        try:
            user = MyUser.objects.get(id=profid)
            school = University.objects.get(id=id)
        except:
            uni = request.user.university.id
            user_id = request.user.id
            return HttpResponseRedirect(reverse('my_profile_sold', args=(uni,user_id)))
        if user.id == request.user.id and school.id == request.user.university.id:
            
            picture = UserPicture.objects.filter(user=user)
            UserPictureFormset = modelformset_factory(UserPicture, form=UserPictureForm, extra=1, max_num=1)
            formset_pic = UserPictureFormset(request.POST or None, request.FILES or None, queryset=picture)
            sold_products = Product.objects.filter(owner=user).filter(university=school).filter(sold=True)
            rating = Rating.objects.filter(profile=user)
            count = Rating.objects.filter(profile=user).count()
            rating_list = []
            if rating:
                for item in rating:
                    rating_list.append(item.number)
                number = sum(rating_list)/float(count)
                rounded_num = round(number * 2.0) / 2.0
            else:
                rounded_num = 0
            user_list = []

            for item in rating:
                user_list.append(item.rater)
            if request.user in user_list:
                rated = 1   

            else:
                rated = 0
            return render_to_response('user_profile/sold_profile.html', locals(), context_instance=RequestContext(request))
        else:
            uni = request.user.university.id
            user_id = request.user.id
            return HttpResponseRedirect(reverse('my_profile_sold', args=(uni,user_id)))
    else:
        return HttpResponseRedirect('/login/')

def profile(request, id, profid):
    if request.user.is_authenticated():
        try:
            user = MyUser.objects.filter(is_active=True).get(id=profid)
            school = University.objects.get(id=id)
        except:
            uni = request.user.university.id
            return HttpResponseRedirect(reverse('main', args=(uni,)))
    
        if request.user != user and request.user.university == school and user.university == request.user.university:

            all_products = Product.objects.filter(owner=user).filter(university=school)
            rating = Rating.objects.filter(profile=user)
            count = Rating.objects.filter(profile=user).count()
            rating_list = []
            if rating:
                for item in rating:
                    rating_list.append(item.number)
                number = sum(rating_list)/float(count)
                rounded_num = round(number * 2.0) / 2.0
            else:
                rounded_num = 0
            user_list = []

            for item in rating:
                user_list.append(item.rater)
            if request.user in user_list:
                rated = 1   

            else:
                rated = 0
            return render_to_response('user_profile/profile.html', locals(), context_instance=RequestContext(request))
        else:
            uni = request.user.university.id
            return HttpResponseRedirect(reverse('main', args=(uni,)))
    else:
        return HttpResponseRedirect('/login/')
    

    

def search(request, id):
    if request.user.is_authenticated():
        try:
            school = University.objects.get(id=id)
        except:
            uni = request.user.university.id
            return HttpResponseRedirect(reverse('main', args=(uni,)))
        if request.user.university == school:
            if request.method == 'GET':
                
                q = request.GET.get('q', '')
                
                products = Product.objects.filter(sold=False).filter(university=school).filter(
                        Q(title__icontains=q) |
                        Q(category__icontains=q)
                    ).exclude(owner=request.user)
            return render_to_response('search-results.html', locals(), context_instance=RequestContext(request))
        else:
            uni = request.user.university.id
            return HttpResponseRedirect(reverse('main', args=(uni,)))
    else:
        return HttpResponseRedirect('/login/')



def category_search(request, id, slug):
    if request.user.is_authenticated():
        try:
            slug=slug
            school = University.objects.get(id=id)
        except:
            uni = request.user.university.id
            return HttpResponseRedirect(reverse('main', args=(uni,)))
        if request.user.university == school:
         
            if slug == 'Newest':
                products = Product.objects.filter(university=school).filter(sold=False).order_by("-timestamp").exclude(owner=request.user)
            else:
                try:
                    category = Category.objects.get(name=slug)
                except:
                    uni = request.user.university.id
                    return HttpResponseRedirect(reverse('main', args=(uni,)))  
                products = Product.objects.filter(university=school).filter(sold=False).filter(category=category).exclude(owner=request.user)
            
            return render_to_response('marketplace/ajax_category_search.html', locals(), context_instance=RequestContext(request))
              
        else:
            uni = request.user.university.id
            return HttpResponseRedirect(reverse('main', args=(uni,)))
    else:
        return HttpResponseRedirect('/login/')

def category_search_price(request, id, slug, param):
    # high = high to low price
    # low = low to high price
    if request.user.is_authenticated():

        try:
            slug=slug
            param=param
            school = University.objects.get(id=id)
        except:
            uni = request.user.university.id
            return HttpResponseRedirect(reverse('main', args=(uni,)))
        if request.user.university == school:
         
            if slug == 'Newest':
                if param == 'High':
                    products = Product.objects.filter(university=school).filter(sold=False).exclude(owner=request.user).order_by("-price")
                if param == 'Low':
                    products = Product.objects.filter(university=school).filter(sold=False).exclude(owner=request.user).order_by("price")
            else:
                try:
                    category = Category.objects.get(name=slug)
                except:
                    uni = request.user.university.id
                    return HttpResponseRedirect(reverse('main', args=(uni,)))

                if param == 'High':
                    products = Product.objects.filter(university=school).filter(sold=False).filter(category=category).exclude(owner=request.user).order_by("-price")
                if param == 'Low':
                    products = Product.objects.filter(university=school).filter(sold=False).filter(category=category).exclude(owner=request.user).order_by("price")
            
            return render_to_response('marketplace/ajax_category_search_price.html', locals(), context_instance=RequestContext(request))
              
        else:
            uni = request.user.university.id
            return HttpResponseRedirect(reverse('main', args=(uni,)))
    else:
        return HttpResponseRedirect('/login/')



def request_user_rating(request):
    if request.method == 'GET':
        
        user = MyUser.objects.get(id=request.user.id)
        rating = Rating.objects.filter(profile=user)
        count = Rating.objects.filter(profile=user).count()
        rating_list = []
        if rating:
            for item in rating:
                rating_list.append(item.number)
            number = sum(rating_list)/float(count)
            rounded_num = round(number * 2.0) / 2.0
        else:
            rounded_num = 0

        response_data = {}
        response_data['rating'] = str(rounded_num)
        new_data = json.dumps(response_data)

        return HttpResponse(new_data, content_type='application/json')


def rating_ajax(request):
    if request.method == 'POST':
        rating_number = request.POST.get('rating_number')
        user = request.POST.get('user')
        request_user = request.POST.get('request_user')
        rater = MyUser.objects.get(email=request_user)
        profile = MyUser.objects.get(email=user)
        r = Rating(rater=rater, profile=profile, number=rating_number)
        r.save()
        response_data = {}
        
        new_data = json.dumps(response_data)

        return HttpResponse(new_data, content_type='application/json')


def product_info_ajax(request):

    if request.method == 'GET':
        prod_id = request.GET.get('prod_info_id')
        
        product = Product.objects.get(id=prod_id)
        user = product.owner
        rating = Rating.objects.filter(profile=user)
        count = Rating.objects.filter(profile=user).count()
        rating_list = []
        if rating:
            for item in rating:
                rating_list.append(item.number)
            number = sum(rating_list)/float(count)
            rounded_num = round(number * 2.0) / 2.0
        else:
            rounded_num = 0
        user_list = []

        for item in rating:
            user_list.append(item.rater)
        if request.user in user_list:
            rated = 1   

        else:
            rated = 0


        return render_to_response('marketplace/prod_info_ajax.html', locals(), context_instance=RequestContext(request))

def add_product(request, id):
    if request.user.is_authenticated():
        try:
            
            school = University.objects.get(id=id)

        except:
            uni = request.user.university.id
            userid = request.user.id
            return HttpResponseRedirect(reverse('my_profile', args=(uni,userid)))
        school = University.objects.get(id=id)
        users = MyUser.objects.filter(is_active=True)
        products = Product.objects.filter(university=school)
        product_form = ProductForm(request.POST or None, request.FILES or None, prefix='product')
        if request.user.university == school:
            if request.method == 'POST':
                
                if product_form.is_valid():
                    title = product_form.cleaned_data['title']
                    category = product_form.cleaned_data['category']
                    price = product_form.cleaned_data['price']
                    description = product_form.cleaned_data['description']
                    
                    condition = product_form.cleaned_data['condition']
                    
                    image = product_form.cleaned_data['image']
                    
                    form3 = product_form.save(commit=False)
                    form3.owner = request.user
                    form3.title = title
                    form3.category = category
                    form3.price = price
                    form3.description = description
                    if image is not None:
                        form3.image = image
                    form3.condition = condition
                    form3.university = school
                    form3.save()

                    response_data = {}


                    response_data['response'] = True
                    
                    new_data = json.dumps(response_data)

                    return HttpResponse(new_data, content_type='application/json')

                else:
                    data = {}
                    data['response'] = False
                    data['errors'] = product_form.errors.as_json()
                    new_data = json.dumps(data)
                    return HttpResponse(new_data, content_type='application/json')
        else:
            uni = request.user.university.id
            return HttpResponseRedirect(reverse('main', args=(uni,)))
    else:
        return HttpResponseRedirect('/login/')
def edit_product(request, schoolid, id):   
    if request.user.is_authenticated():
        try:
            product = Product.objects.get(id=id)
            school = University.objects.get(id=schoolid)
        except:
            uni = request.user.university.id
            userid = request.user.id
            return HttpResponseRedirect(reverse('my_profile', args=(uni,userid)))
        if product.owner == request.user:
            users = MyUser.objects.filter(is_active=True)
            edit_product_form = EditProductForm(request.POST or None, request.FILES or None, prefix='product')
            if request.method == 'POST':

                if edit_product_form.is_valid(): 

                    price = edit_product_form.cleaned_data['price']
                    title = edit_product_form.cleaned_data['title']
                    image = edit_product_form.cleaned_data['image']
                    condition = edit_product_form.cleaned_data['condition']
                    description = edit_product_form.cleaned_data['description']
                    category = edit_product_form.cleaned_data['category']
                    product.price = price
                    product.title = title
                    product.category = category
                    product.condition = condition
                    product.description = description
                    if image is not None:
                        product.image = image
                    product.save()
                    response_data = {}

                    response_data['response'] = True

                    new_data = json.dumps(response_data)

                    return HttpResponse(new_data, content_type='application/json')
                else:
                    data = {}
                    data['response'] = False
                    data['errors'] = edit_product_form.errors.as_json()
                    new_data = json.dumps(data)
                    return HttpResponse(new_data, content_type='application/json')
        else:
            uni = request.user.university.id
            userid = request.user.id
            return HttpResponseRedirect(reverse('my_profile', args=(uni,userid)))
    else:
        return HttpResponseRedirect('/login/')

def sold(request):
    
    if request.method =='POST':
        user = request.user
        product_id = request.POST.get('product_id')
            
        
        obj = Product.objects.get(id=product_id)
        


        response_data = {}
        response_data['id'] = obj.id

        obj.sold = True
        obj.save()

        new_data = json.dumps(response_data)
        
        return HttpResponse(new_data, content_type='application/json')


def account_history_sold(request):
    if request.user.is_authenticated():
        products = Product.objects.filter(owner=request.user).filter(sold=True)

        return render_to_response('marketplace/account_history_sold.html', locals(), context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/login/')

def account_history_selling(request):
    if request.user.is_authenticated():
        products = Product.objects.filter(owner=request.user).filter(sold=False)
        
        return render_to_response('marketplace/account_history_selling.html', locals(), context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/login/')

def registration_complete(request):
    
    return render_to_response('register_complete.html', locals(), context_instance=RequestContext(request))


def register_confirm(request, activation_key):
    #check if user is already logged in and if he is redirect him to some other url, e.g. home
    if request.user.is_authenticated():
        uni = request.user.university.id
        HttpResponseRedirect(reverse('main', args=(uni)))
        

    # check if there is UserProfile which matches the activation key (if not then display 404)
    user_profile = get_object_or_404(UserProfile, activation_key=activation_key)

    #check if the activation key has expired, if it hase then render confirm_expired.html
    
    #if the key hasn't expired save user and set him as active and render some template to confirm activation
    user = user_profile.user
    user.is_active = True
    user.save()
    login_form = LoginForm(request.POST or None)
    return render_to_response('user_profile/confirm.html', locals(), context_instance=RequestContext(request))

def auth_login(request):
    login_form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            if user is not None:

                login(request, user)

                user = request.user
                
                
                response_data = {}
                response_data['success'] = 'True'

                response_data['url'] = '/'+str(request.user.id)+'/profile_pic_login/'
                new_data = json.dumps(response_data)

                return HttpResponse(new_data, content_type='application/json')
               
                
        else:
            response_data = {}
            response_data['success'] = 'False'
            
            new_data = json.dumps(response_data)

            return HttpResponse(new_data, content_type='application/json')

def edit_prof_pic(request):
    user = request.user
    
    UserPictureFormset = modelformset_factory(UserPicture, form=UserPictureForm, extra=1, max_num=1)
    formset_pic = UserPictureFormset(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        
        
        if formset_pic.is_valid():
            for form in formset_pic:
                form3 = form.save(commit=False)
                form3.user = request.user
                form3.save()
                
                response_data = {}
                response_data['response'] = True
                new_data = json.dumps(response_data)
                    
                return HttpResponse(new_data, content_type='application/json')
        else:
            data = {}
            data['response'] = False
            new_data = json.dumps(data)
            return HttpResponse(new_data, content_type='application/json')

def profile_pic_login(request, id):
    if request.user.is_authenticated():
        try:
            user = MyUser.objects.get(id=id)
        except:
            user_id = request.user.id
            return HttpResponseRedirect(reverse('profile_pic_login', args=(user_id,)))
        if not UserPicture.objects.filter(user=user).exists():
            if request.user == user:
                picture = UserPicture.objects.filter(user=user)
                UserPictureFormset = modelformset_factory(UserPicture, form=UserPictureForm, extra=1, max_num=1)
                formset_pic = UserPictureFormset(request.POST or None, request.FILES or None, queryset=picture)
                return render_to_response('user_profile/profile_pic_login.html', locals(), context_instance=RequestContext(request))
            else:
                user_id = request.user.id
                return HttpResponseRedirect(reverse('profile_pic_login', args=(user_id,)))
        else:
            user_id = request.user.id
            return HttpResponseRedirect(reverse('provide_service_login', args=(user_id,)))
    else:
        return HttpResponseRedirect('/login/')
    

def provide_service_login(request, id):
    user = MyUser.objects.get(id=id)

    if not DoService.objects.filter(user=user).exists():
        if request.user == user:
            return render_to_response('provide_service_login.html', locals(), context_instance=RequestContext(request))
        else:
            user_id = request.user.id
            return HttpResponseRedirect(reverse('provide_service_login', args=(user_id,)))
    else:
        user_id = request.user.id
        return HttpResponseRedirect(reverse('want_service_login', args=(user_id,)))



def want_service_login(request, id):          
    user = MyUser.objects.get(id=id)
    if not WantService.objects.filter(user=user).exists():
        if request.user == user:
            return render_to_response('want_service_login.html', locals(), context_instance=RequestContext(request))
        else:
            user_id = request.user.id
            return HttpResponseRedirect(reverse('want_service_login', args=(user_id,)))
    else:
        user_id = request.user.id
        return HttpResponseRedirect(reverse('main', args=(user_id,)))

def error_login(request):          
    
    return render_to_response('login.html', locals(), context_instance=RequestContext(request))

def auth_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def messages_count(request):
    convos = Convo.objects.filter(primary_user=request.user)
    unread = DirectMessage.objects.filter(receiver=request.user).filter(read=False)
    
    count_list = []
    for item1 in unread:
        for item2 in convos:
            if item1.sender.id == item2.secondary_user.id:
                count_list.append(item1)
    count = len(count_list)
    note_json = {}
    note_json['count'] = count
    
    data = json.dumps(note_json)
        

    return HttpResponse(data, content_type='application/json')

def matching_profile_do(request, id, profid):
    if request.user.is_authenticated():
        try:
            user = MyUser.objects.get(id=profid)
            school = University.objects.get(id=id)
        except:
            uni = request.user.university.id
            user_id = request.user.id
            return HttpResponseRedirect(reverse('matching_profile', args=(uni,user_id)))

        if user.id == request.user.id and school.id == request.user.university.id:

            if DoService.objects.filter(user=user).exists():
                do_service = DoService.objects.filter(user=user)
                DoServiceFormset = modelformset_factory(DoService, form=DoServiceForm, extra=2, max_num=1)
                formset_d = DoServiceFormset(request.POST or None, queryset=do_service)
                want_service = WantService.objects.filter(user=user)
                WantServiceFormset = modelformset_factory(WantService, form=WantServiceForm, extra=1, max_num=1)
                formset_w = WantServiceFormset(request.POST or None, queryset=want_service)
                
                what_i_offer_to_do = DoService.objects.get(user=request.user)
                    
                what_people_want_done = WantService.objects.filter(university=school).exclude(user=request.user)

                
                

                a_list = what_i_offer_to_do.name.all()
                b_list = what_people_want_done

                # athletic queryset

                what_people_want_athletic = []
                user_list_want_athletic = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Athletic Trainer':
                                    what_people_want_athletic.append(item_want.name)
                                    user_list_want_athletic.append(item_name.user)


                a = zip(what_people_want_athletic, user_list_want_athletic)
                    
                want_list_athletic = set(a)

                # bartender queryset

                what_people_want_bartender = []
                user_list_want_bartender = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Bartender':
                                    what_people_want_bartender.append(item_want.name)
                                    user_list_want_bartender.append(item_name.user)


                b = zip(what_people_want_bartender, user_list_want_bartender)
                    
                want_list_bartender = set(b)

                 # chef queryset
                what_people_want_chef = []
                user_list_want_chef = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Chef':
                                    what_people_want_chef.append(item_want.name)
                                    user_list_want_chef.append(item_name.user)


                c = zip(what_people_want_chef, user_list_want_chef)
                    
                want_list_chef = set(c)

                 # driver queryset
                what_people_want_driver = []
                user_list_want_driver = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Driver':
                                    what_people_want_driver.append(item_want.name)
                                    user_list_want_driver.append(item_name.user)


                d = zip(what_people_want_driver, user_list_want_driver)
                    
                want_list_driver = set(d)

                # delivery driver
                what_people_want_delivery_driver = []
                user_list_want_delivery_driver = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Delivery Driver':
                                    what_people_want_delivery_driver.append(item_want.name)
                                    user_list_want_delivery_driver.append(item_name.user)


                e = zip(what_people_want_delivery_driver, user_list_want_delivery_driver)
                    
                want_list_delivery_driver = set(e)

                #cleaning
                what_people_want_cleaning = []
                user_list_want_cleaning = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Cleaning':
                                    what_people_want_cleaning.append(item_want.name)
                                    user_list_want_cleaning.append(item_name.user)


                f = zip(what_people_want_cleaning, user_list_want_cleaning)
                    
                want_list_cleaning = set(f)

                what_people_want_laundry = []
                user_list_want_laundry = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Laundry':
                                    what_people_want_laundry.append(item_want.name)
                                    user_list_want_laundry.append(item_name.user)


                g = zip(what_people_want_laundry, user_list_want_laundry)
                    
                want_list_laundry = set(g)

                what_people_want_interior = []
                user_list_want_interior = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Interior Designer':
                                    what_people_want_interior.append(item_want.name)
                                    user_list_want_interior.append(item_name.user)


                h = zip(what_people_want_interior, user_list_want_interior)
                    
                want_list_interior = set(h)

                what_people_want_moving = []
                user_list_want_moving = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Moving':
                                    what_people_want_moving.append(item_want.name)
                                    user_list_want_moving.append(item_name.user)


                i = zip(what_people_want_moving, user_list_want_moving)
                    
                want_list_moving = set(i)

                what_people_want_musician = []
                user_list_want_musician = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Musician':
                                    what_people_want_musician.append(item_want.name)
                                    user_list_want_musician.append(item_name.user)


                j = zip(what_people_want_musician, user_list_want_musician)
                    
                want_list_musician = set(j)

                # DJ

                what_people_want_dj = []
                user_list_want_dj = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'D.J.':
                                    what_people_want_dj.append(item_want.name)
                                    user_list_want_dj.append(item_name.user)


                k = zip(what_people_want_dj, user_list_want_dj)
                    
                want_list_dj = set(k)

                # Comedian

                what_people_want_comedian = []
                user_list_want_comedian = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Comedian':
                                    what_people_want_comedian.append(item_want.name)
                                    user_list_want_comedian.append(item_name.user)


                l = zip(what_people_want_comedian, user_list_want_comedian)
                    
                want_list_comedian = set(l)

                # English

                what_people_want_english = []
                user_list_want_english = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'English':
                                    what_people_want_english.append(item_want.name)
                                    user_list_want_english.append(item_name.user)


                m = zip(what_people_want_english, user_list_want_english)
                    
                want_list_english = set(m)

                # History

                what_people_want_history = []
                user_list_want_history = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'History':
                                    what_people_want_history.append(item_want.name)
                                    user_list_want_history.append(item_name.user)


                n = zip(what_people_want_history, user_list_want_history)
                    
                want_list_history = set(n)

                # Business

                what_people_want_business = []
                user_list_want_business = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Business':
                                    what_people_want_business.append(item_want.name)
                                    user_list_want_business.append(item_name.user)


                o = zip(what_people_want_business, user_list_want_business)
                    
                want_list_business = set(o)

                # Math

                what_people_want_math = []
                user_list_want_math = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Math':
                                    what_people_want_math.append(item_want.name)
                                    user_list_want_math.append(item_name.user)


                p = zip(what_people_want_math, user_list_want_math)
                    
                want_list_math = set(p)

                # Science

                what_people_want_science = []
                user_list_want_science = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Science':
                                    what_people_want_science.append(item_want.name)
                                    user_list_want_science.append(item_name.user)


                q = zip(what_people_want_science, user_list_want_science)
                    
                want_list_science = set(q)

                # I.T.

                what_people_want_it = []
                user_list_want_it = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'I.T. Help':
                                    what_people_want_it.append(item_want.name)
                                    user_list_want_it.append(item_name.user)


                r = zip(what_people_want_it, user_list_want_it)
                    
                want_list_it = set(r)

                # Odd Jobs

                what_people_want_odd = []
                user_list_want_odd = []

                for item_name in b_list:
                    
                    for item_want in item_name.name.all():
                        for do in a_list:
                            if item_want.name == do.name:
                                if item_want.name == 'Odd Jobs':
                                    what_people_want_odd.append(item_want.name)
                                    user_list_want_odd.append(item_name.user)


                s = zip(what_people_want_odd, user_list_want_odd)
                    
                want_list_odd = set(s)


                do_checkbox = what_i_offer_to_do.name.all()

                do_checkbox_list = []

                for item in do_checkbox:
                    do_checkbox_list.append(item.name)



                json_do_list = json.dumps(do_checkbox_list)
            else:
                json_do_list = json.dumps(False)
            
      
            return render_to_response('matching/matching-profile.html', locals(), context_instance=RequestContext(request))
        else:
            uni = request.user.university.id
            user_id = request.user.id
            return HttpResponseRedirect(reverse('matching_profile', args=(uni,user_id)))
    else:
        return HttpResponseRedirect('/login/')   

def matching_profile_want(request, id, profid):
    if request.user.is_authenticated():
        try:
            user = MyUser.objects.get(id=profid)
            school = University.objects.get(id=id)
        except:
            uni = request.user.university.id
            user_id = request.user.id
            return HttpResponseRedirect(reverse('matching_profile', args=(uni,user_id)))

        if user.id == request.user.id and school.id == request.user.university.id:

        
            if WantService.objects.filter(user=request.user).exists():
                want_service = WantService.objects.filter(user=user)
                WantServiceFormset = modelformset_factory(WantService, form=WantServiceForm, extra=1, max_num=1)
                formset_w = WantServiceFormset(request.POST or None, queryset=want_service)


                what_i_want = WantService.objects.get(user=request.user)
                        
                what_people_do = DoService.objects.filter(university=school).exclude(user=request.user)

                
                c_list = what_i_want.name.all()
                d_list = what_people_do

                # athletic queryset

                what_people_will_do_athletic = []
                user_list_do_athletic = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Athletic Trainer':
                                    what_people_will_do_athletic.append(item_do.name)
                                    user_list_do_athletic.append(item_name.user)


                a = zip(what_people_will_do_athletic, user_list_do_athletic)
                    
                do_list_athletic = set(a)

                # bartender queryset

                what_people_will_do_bartender = []
                user_list_do_bartender = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Bartender':
                                    what_people_will_do_bartender.append(item_do.name)
                                    user_list_do_bartender.append(item_name.user)


                b = zip(what_people_will_do_bartender, user_list_do_bartender)

                do_list_bartender = set(b)

                # chef queryset

                what_people_will_do_chef = []
                user_list_do_chef = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Chef':
                                    what_people_will_do_chef.append(item_do.name)
                                    user_list_do_chef.append(item_name.user)


                c = zip(what_people_will_do_chef, user_list_do_chef)

                do_list_chef = set(c)

                # driver queryset

                what_people_will_do_driver = []
                user_list_do_driver = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Driver':
                                    what_people_will_do_driver.append(item_do.name)
                                    user_list_do_driver.append(item_name.user)


                d = zip(what_people_will_do_driver, user_list_do_driver)

                do_list_driver = set(d)

                # delivery driver queryset

                what_people_will_do_delivery = []
                user_list_do_delivery = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Delivery Driver':
                                    what_people_will_do_delivery.append(item_do.name)
                                    user_list_do_delivery.append(item_name.user)


                e = zip(what_people_will_do_delivery, user_list_do_delivery)

                do_list_delivery = set(e)

                 # cleaning queryset

                what_people_will_do_cleaning = []
                user_list_do_cleaning = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Cleaning':
                                    what_people_will_do_cleaning.append(item_do.name)
                                    user_list_do_cleaning.append(item_name.user)


                f = zip(what_people_will_do_cleaning, user_list_do_cleaning)

                do_list_cleaning = set(f)

                # laundry queryset

                what_people_will_do_laundry = []
                user_list_do_laundry = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Laundry':
                                    what_people_will_do_laundry.append(item_do.name)
                                    user_list_do_laundry.append(item_name.user)


                g = zip(what_people_will_do_laundry, user_list_do_laundry)

                do_list_laundry = set(g)

                # interior designer queryset

                what_people_will_do_designer = []
                user_list_do_designer = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Interior Designer':
                                    what_people_will_do_designer.append(item_do.name)
                                    user_list_do_designer.append(item_name.user)


                h = zip(what_people_will_do_designer, user_list_do_designer)

                do_list_designer = set(h)

                # moving queryset

                what_people_will_do_moving = []
                user_list_do_moving = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Moving':
                                    what_people_will_do_moving.append(item_do.name)
                                    user_list_do_moving.append(item_name.user)


                i = zip(what_people_will_do_moving, user_list_do_moving)

                do_list_moving = set(i)

                # musician queryset

                what_people_will_do_musician = []
                user_list_do_musician = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Musician':
                                    what_people_will_do_musician.append(item_do.name)
                                    user_list_do_musician.append(item_name.user)


                j = zip(what_people_will_do_musician, user_list_do_musician)

                do_list_musician = set(j)

                # dj queryset

                what_people_will_do_dj = []
                user_list_do_dj = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'D.J.':
                                    what_people_will_do_dj.append(item_do.name)
                                    user_list_do_dj.append(item_name.user)


                k = zip(what_people_will_do_dj, user_list_do_dj)

                do_list_dj = set(k)

                # comedian queryset

                what_people_will_do_comedian = []
                user_list_do_comedian = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Comedian':
                                    what_people_will_do_comedian.append(item_do.name)
                                    user_list_do_comedian.append(item_name.user)


                l = zip(what_people_will_do_comedian, user_list_do_comedian)

                do_list_comedian = set(l)

                # english queryset

                what_people_will_do_english = []
                user_list_do_english = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'English':
                                    what_people_will_do_english.append(item_do.name)
                                    user_list_do_english.append(item_name.user)


                m = zip(what_people_will_do_english, user_list_do_english)

                do_list_english = set(m)

                # history queryset

                what_people_will_do_history = []
                user_list_do_history = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'History':
                                    what_people_will_do_history.append(item_do.name)
                                    user_list_do_history.append(item_name.user)


                n = zip(what_people_will_do_history, user_list_do_history)

                do_list_history = set(n)

                # business queryset

                what_people_will_do_business = []
                user_list_do_business = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Business':
                                    what_people_will_do_business.append(item_do.name)
                                    user_list_do_business.append(item_name.user)


                o = zip(what_people_will_do_business, user_list_do_business)

                do_list_business = set(o)

                # math queryset

                what_people_will_do_math = []
                user_list_do_math = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Math':
                                    what_people_will_do_math.append(item_do.name)
                                    user_list_do_math.append(item_name.user)


                p = zip(what_people_will_do_math, user_list_do_math)

                do_list_math = set(p)

                # science queryset

                what_people_will_do_science = []
                user_list_do_science = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Science':
                                    what_people_will_do_science.append(item_do.name)
                                    user_list_do_science.append(item_name.user)


                q = zip(what_people_will_do_science, user_list_do_science)

                do_list_science = set(q)

                # it queryset

                what_people_will_do_it = []
                user_list_do_it = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'I.T. Help':
                                    what_people_will_do_it.append(item_do.name)
                                    user_list_do_it.append(item_name.user)


                r = zip(what_people_will_do_it, user_list_do_it)

                do_list_it = set(r)

                # odd queryset

                what_people_will_do_odd = []
                user_list_do_odd = []

                for item_name in d_list:
                    
                    for item_do in item_name.name.all():
                        for want in c_list:
                            if item_do.name == want.name:
                                if item_do.name == 'Odd Jobs':
                                    what_people_will_do_odd.append(item_do.name)
                                    user_list_do_odd.append(item_name.user)


                s = zip(what_people_will_do_odd, user_list_do_odd)

                do_list_odd = set(s)

                want_checkbox = what_i_want.name.all()

                want_checkbox_list = []

                for item in want_checkbox:
                    want_checkbox_list.append(item.name)

                json_want_list = json.dumps(want_checkbox_list)

            else:
                json_want_list = json.dumps(False)
      
            return render_to_response('matching/matching-profile-want.html', locals(), context_instance=RequestContext(request))
        else:
            uni = request.user.university.id
            user_id = request.user.id
            return HttpResponseRedirect(reverse('matching_profile_want', args=(uni,user_id)))
    else:
        return HttpResponseRedirect('/login/')   

def do_service(request, id):

    user = MyUser.objects.get(id=id)
    do_service = DoService.objects.filter(user=user)
    do_service_form = DoServiceForm(request.POST or None)

    if request.method == 'POST':
        some_var = request.POST.getlist('do-check')
        
        

        if DoService.objects.filter(user=request.user).exists():
            doservice = DoService.objects.get(user=request.user)
            all_service = doservice.name.all()

            all_service_type = []

            for item in all_service:
                all_service_type.append(ServiceType.objects.get(name=item.name))

            for item in all_service_type:
                doservice.name.remove(item)

            service_type = []

            for item in some_var:
                service_type.append(ServiceType.objects.get(name=item))

            for item in service_type:
                doservice.name.add(item)

            response_data = {}




            new_data = json.dumps(response_data)

            return HttpResponse(new_data, content_type='application/json')
        else:
            some_var = request.POST.getlist('do-check')
            doservice = DoService.objects.create(user=request.user, university=request.user.university)
            
            service_type = []
            for item in some_var:
                service_type.append(ServiceType.objects.get(name=item))

            for item in service_type:
                doservice.name.add(item)

            response_data = {}




            new_data = json.dumps(response_data)

            return HttpResponse(new_data, content_type='application/json')


def want_service(request, id):

    user = MyUser.objects.get(id=id)
    want_service = WantService.objects.filter(user=user)
    want_service_form = WantServiceForm(request.POST or None)

    if request.method == 'POST':
        some_var = request.POST.getlist('want-check')

        if WantService.objects.filter(user=request.user).exists():
            wantservice = WantService.objects.get(user=request.user)
            all_service = wantservice.name.all()
            all_service_type = []

            for item in all_service:
                all_service_type.append(WantServiceType.objects.get(name=item.name))

            for item in all_service_type:
                wantservice.name.remove(item)

            service_type = []
            for item in some_var:
                service_type.append(WantServiceType.objects.get(name=item))

            for item in service_type:
                wantservice.name.add(item)

            response_data = {}




            new_data = json.dumps(response_data)

            return HttpResponse(new_data, content_type='application/json')
        else:
            some_var = request.POST.getlist('want-check')
            wantservice = WantService.objects.create(user=request.user, university=request.user.university)
            
            service_type = []
            for item in some_var:
                service_type.append(WantServiceType.objects.get(name=item))

            for item in service_type:
                wantservice.name.add(item)

            response_data = {}




            new_data = json.dumps(response_data)

            return HttpResponse(new_data, content_type='application/json')