from django.db import models

from django.contrib.auth.models import AbstractUser

from django.db.models.signals import post_save

from random import randint

class User(AbstractUser):

    is_verified=models.BooleanField(default=False)

    otp=models.CharField(max_length=6,null=True,blank=True)

    phone=models.CharField(max_length=10,null=True)

    def generate_otp(self):

        self.otp=str(randint(1000,9000))+str(self.id)

        self.save()

class BaseModel(models.Model):

    created_at=models.DateTimeField(auto_now_add=True)

    updated_at=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

class Category(BaseModel):

    name=models.CharField(max_length=100)

    def __str__(self):

        return self.name
    
class Book(BaseModel):

    title = models.CharField(max_length=200)

    author=models.CharField(max_length=200)

    category_object = models.ForeignKey(Category,on_delete=models.CASCADE)

    summary = models.TextField()

    isbn = models.CharField(max_length=13, unique=True)

    publication_date=models.DateField()

    no_of_pages=models.PositiveIntegerField()

    price = models.PositiveIntegerField()

    stock = models.PositiveIntegerField(default=0)

    cover_image = models.ImageField(upload_to="book_covers", blank=True, null=True)

    def __str__(self):

        return self.title
    
class Kindle(models.Model):

    book = models.OneToOneField(Book,on_delete=models.CASCADE,related_name='kindle')

    kindle_price = models.PositiveIntegerField()

    pdf_file=models.FileField(upload_to='kindle_books')

    def __str__(self):

        return self.book.title
    
class Basket(BaseModel):

    owner=models.OneToOneField(User,on_delete=models.CASCADE,related_name="cart")
    
class BasketItem(BaseModel):

    book_object=models.ForeignKey(Book,on_delete=models.CASCADE)

    quantity=models.PositiveIntegerField(default=1)

    is_order_placed=models.BooleanField(default=False)

    basket_object=models.ForeignKey(Basket,on_delete=models.CASCADE,related_name="cart_item")


def create_basket(sender,instance,created,**kwargs):

    if created:

        Basket.objects.create(owner=instance)

post_save.connect(create_basket,User)

