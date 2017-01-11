from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
import datetime
from django.utils import timezone
from django.core.files.base import ContentFile
from PIL import Image, ExifTags
from io import BytesIO

class MyUserManager(BaseUserManager):
    def create_user(self, username=None, email=None, first_name=None, last_name=None, password=None, referral=None):
        """
        Creates and saves a User with the given email, first name, last name and password.
        """
        
        
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            referral=referral,
            
            
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given email, first name, last name and password.
        """
        user = self.create_user(
            username=username,
            email=email,
            password=password,
            
            
        )
        user.is_admin = True
        user.is_active = True
        
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=120, null=True, blank=True)
    first_name = models.CharField(max_length=120, null=True, blank=True)
    last_name = models.CharField(max_length=120, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    university = models.ForeignKey('University', null=True, blank=True)
    referral = models.CharField(max_length=120, null=True, blank=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    

    def get_full_name(self):
        # The user is identified by their email address
        return "% %" %(self.first_name, self.last_name)

    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

    def __unicode__(self):         
        return self.email

    def get_absolute_url(self):
        return reverse("profile", kwargs={"id":self.id})

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    
class UserProfile(models.Model):
    user = models.OneToOneField(MyUser)
    activation_key = models.CharField(max_length=40, blank=True)
    key_expires = models.DateTimeField(default=datetime.date.today())
      
    def __unicode__(self):
        return self.user.email

    class Meta:
        verbose_name_plural=u'User profiles'

class Rating(models.Model):
    rater = models.ForeignKey(MyUser, related_name='rater')
    profile = models.ForeignKey(MyUser, related_name='profile')
    number = models.IntegerField(default=0)
        
    def __unicode__(self):         
        return str(self.rater)

class University(models.Model):
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    longitude = models.CharField(max_length=200, null=True, blank=True)
    latitude = models.CharField(max_length=200, null=True, blank=True)


    def __unicode__(self):         
        return self.name

class UserPicture(models.Model):
    user = models.ForeignKey(MyUser)
    image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    
    def __unicode__(self, ):
        return str(self.image)
    def save(self, *args, **kwargs):
        if self.image:
            pil_image_obj = Image.open(self.image)
            format = pil_image_obj.format
            w,h = pil_image_obj.size
            if w > h:
                ratio = h/float(w)
                
                newWidth = 650
                newHeight = int(round(newWidth * float(ratio)))

                new_image = pil_image_obj.resize((newWidth,newHeight), Image.ANTIALIAS)

                
            elif h > w:
                 
                ratio = w/float(h)
            
                newHeight = 650
                newWidth = int(round(newHeight * float(ratio)))

                new_image = pil_image_obj.resize((newWidth,newHeight), Image.ANTIALIAS)
            elif h==w:
                
                ratio = h/float(w)
                
                newWidth = 650
                newHeight = int(round(newWidth * float(ratio)))

                new_image = pil_image_obj.resize((newWidth,newHeight), Image.ANTIALIAS)


            try:
                pil_image_obj = Image.open(self.image)
                exif_data = pil_image_obj._getexif()
                for k,v in exif_data.items():

                    if k == int("274"):
                        
                        if v == int("3"):

                            
                            new_image = new_image.rotate(180, expand=True)
                            
                            

                                
                        if v == int("6"):
                            
                            
                            new_image = new_image.rotate(270, expand=True)
                            
                new_image_io = BytesIO()
                new_image.save(new_image_io, optimize=True, quality=95, format=format)

                temp_name = self.image.name
                self.image.delete(save=False)  

                self.image.save(
                    temp_name,
                    content=ContentFile(new_image_io.getvalue()),
                    save=False
                )

            except:
                new_image = new_image
                new_image_io = BytesIO()
                new_image.save(new_image_io, optimize=True, quality=95, format=format)

                temp_name = self.image.name
                self.image.delete(save=False)  

                self.image.save(
                    temp_name,
                    content=ContentFile(new_image_io.getvalue()),
                    save=False
                )
            
            super(UserPicture, self).save(*args, **kwargs)
        else:
            super(UserPicture, self).save(*args, **kwargs)
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20)
    body = models.CharField(max_length=3000)

    def __unicode__(self, ):
        return str(self.name)