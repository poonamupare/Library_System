from rest_framework import serializers
from .models import User, Book, BorrowRequest
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_librarian']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'copies_available']

class BorrowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRequest
        fields = ['id', 'user', 'book', 'date_from', 'date_to', 'status']

class BorrowRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRequest
        fields = ['book', 'date_from', 'date_to']

    def validate(self, data):
        book = data['book']
        date_from = data['date_from']
        date_to = data['date_to']

        if BorrowRequest.objects.filter(
            book=book,
            status='Approved',
            date_to__gte=date_from,
            date_from__lte=date_to
        ).exists():
            raise serializers.ValidationError("The book is already borrowed during the requested period.")

        return data