from django.contrib import admin
from bookapp.models import Category,Book,Kindle,User


admin.site.register(User)
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(Kindle)
