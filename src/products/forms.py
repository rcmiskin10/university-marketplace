from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms.models import ModelForm
from .models import Product, DoService, ServiceType, WantService, WantServiceType
from django.forms.widgets import CheckboxSelectMultiple
from PIL import Image, ExifTags

CON_CHOICES =(
    ('New', 'New'),
    ('Used', 'Used'),
)

CAT_CHOICES =(
    ('Textbooks', 'Textbooks'),
    ('Apparel', 'Apparel'),
    ('Electronics', 'Electronics'),
    ('Furniture', 'Furniture'),
    ('Sublet', 'Sublet'),
    ('Tutors', 'Tutors'),
    ('Other', 'Other'),
)

MAX_UPLOAD_SIZE = "5242880"

class ProductForm(forms.ModelForm):
    def __init__(self, data=None, files=None, **kwargs):
        super(ProductForm, self).__init__(data, files, kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.add_input(Submit('submit', 'Add Product', css_class='btn btn-primary'))
     
    title = forms.CharField(label='', required=True,
                            widget=forms.TextInput( attrs={'placeholder': 'Title: 50 character limit.'} ))
    category = forms.ChoiceField(choices = CAT_CHOICES, label="", initial='', widget=forms.Select(), required=True)
    condition = forms.ChoiceField(choices = CON_CHOICES, label="", initial='', widget=forms.Select(), required=True)
    price = forms.DecimalField(label='', required=True,
                            widget=forms.TextInput( attrs={'placeholder': 'Price'} ))
    condition = forms.CharField(label='', required=True,
                            widget=forms.TextInput( attrs={'placeholder': 'Condition'} ))
    image = forms.ImageField(required=False)
    class Meta:
        model = Product
        fields = ['image', 'category', 'title', 'description', 'price']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price > 100000:
            raise forms.ValidationError("Sorry, the price was invalid. Needs to be < 100k.")
        if price < 0:
            raise forms.ValidationError("Sorry, the price was invalid. Needs to be positive.")
        return price
    def clean_title(self):
        title = self.cleaned_data.get('title')
        length = len(title)
        if length >200:
            raise forms.ValidationError("Title needs to be < 200 characters long.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        length = len(description)
        if length >200:
            raise forms.ValidationError("Description needs to be < 200 characters long.")
        return description

class EditProductForm(forms.ModelForm):
    def __init__(self, data=None, files=None, **kwargs):
        super(EditProductForm, self).__init__(data, files, kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.add_input(Submit('submit', 'Add Product', css_class='btn btn-primary'))
     
    title = forms.CharField(label='', required=False,
                            widget=forms.TextInput( attrs={'placeholder': 'Title: 50 character limit.'} ))
    category = forms.ChoiceField(choices = CAT_CHOICES, label="", initial='', widget=forms.Select(), required=False)
    condition = forms.ChoiceField(choices = CON_CHOICES, label="", initial='', widget=forms.Select(), required=False)
    price = forms.DecimalField(label='', required=False,
                            widget=forms.TextInput( attrs={'placeholder': 'Price'} ))
    
    image = forms.ImageField(required=False)
    class Meta:
        model = Product
        fields = ['image', 'category', 'title', 'description', 'price']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price > 100000:
            raise forms.ValidationError("Sorry, the price was invalid. Needs to be < 100k.")
        if price < 0:
            raise forms.ValidationError("Sorry, the price was invalid. Needs to be positive.")
        return price
    def clean_title(self):
        title = self.cleaned_data.get('title')
        length = len(title)
        if length >200:
            raise forms.ValidationError("Title needs to be < 200 characters long.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        length = len(description)
        if length >200:
            raise forms.ValidationError("Description needs to be < 200 characters long.")
        return description

class DoServiceForm(forms.ModelForm):
    
    class Meta:
        model = DoService
        fields = ('name',)
             
    

class WantServiceForm(forms.ModelForm):
    
    class Meta:
        model = WantService
        fields = ('name',)
             
    