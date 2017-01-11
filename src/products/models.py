
from django.db import models
from accounts.models import MyUser, University
from PIL import Image, ExifTags
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django import forms
MAX_UPLOAD_SIZE = "5242880"
class Product(models.Model):
	
	CON_CHOICES = (
		('New', 'New'),
		('Used', 'Used'),
        
	)

	CAT_CHOICES = (
		('Textbooks', 'Textbooks'),
		('Apparel', 'Apparel'),
		('Electronics', 'Electronics'),
		('Furniture', 'Furniture'),
		('Sublet', 'Sublet'),
		('Tutors', 'Tutors'),
		('Other', 'Other'),
	)
	owner = models.ForeignKey(MyUser, null=True, blank=True)
	title = models.CharField(max_length=200, null=True, blank=True)
	description = models.CharField(max_length=200, null=True, blank=True)
	category = models.CharField(max_length=20, choices=CAT_CHOICES, null=True, blank=True)
	price = models.DecimalField(max_digits=20, decimal_places=2,null=True, blank=True)
	order = models.IntegerField(default=0)
	sold = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False, null=True, blank=True)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True, null=True, blank=True)
	image = models.ImageField(upload_to="products/", null=True, blank=True)
	condition = models.CharField(max_length=10, choices=CON_CHOICES, null=True, blank=True)
	university = models.ForeignKey(University, null=True, blank=True)


	def __unicode__(self):
	    return str(self.title)

	class Meta:
	    ordering = ['-order']
	

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
			
			super(Product, self).save(*args, **kwargs)
		else:
			super(Product, self).save(*args, **kwargs)
class Category(models.Model):
	name = models.CharField(max_length=50)

	def __unicode__(self):
	    return str(self.name)

class DoService(models.Model):
	user = models.ForeignKey(MyUser, null=True, blank=True)
	name = models.ManyToManyField('ServiceType', related_name='do_service_type', null=True, blank=True)
	university = models.ForeignKey(University, null=True, blank=True)
	def __unicode__(self):
		return str(self.user)

class WantService(models.Model):
	user = models.ForeignKey(MyUser, null=True, blank=True)
	name = models.ManyToManyField('WantServiceType', related_name='want_service_type', null=True, blank=True)
	university = models.ForeignKey(University, null=True, blank=True)
	def __unicode__(self):
		return str(self.user)



class WantServiceType(models.Model):
	name = models.CharField(max_length=250, null=True, blank=True)

	def __unicode__(self):
	    return self.name

class ServiceType(models.Model):
	name = models.CharField(max_length=250, null=True, blank=True)

	def __unicode__(self):
	    return self.name





