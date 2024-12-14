from django.contrib import admin

# Register your models here.
from django.contrib import admin

from library.models import User, Book, BorrowRequest

admin.site.register(User)
admin.site.register(Book)
admin.site.register(BorrowRequest)