import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    UserSerializer, 
    BookSerializer, 
    BorrowRequestSerializer, 
    BorrowRequestCreateSerializer
)
from .models import User, Book, BorrowRequest

# Librarian: Create a new library user
class CreateUserView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_librarian:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=request.data['password'],
                is_librarian=serializer.validated_data['is_librarian']
            )
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Library User: Get list of users
class UserListView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
class AddBookView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_librarian:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.save()  # Save the validated book data
            return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Librarian: View all borrow requests
class LibrarianBorrowRequestView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_librarian:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        borrow_requests = BorrowRequest.objects.all()
        serializer = BorrowRequestSerializer(borrow_requests, many=True)
        return Response(serializer.data)

# Librarian: Approve or deny a borrow request
class ManageBorrowRequestView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        if not request.user.is_librarian:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            borrow_request = BorrowRequest.objects.get(id=request_id)
        except BorrowRequest.DoesNotExist:
            return Response({'error': 'Borrow request not found.'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action == 'approve':
            borrow_request.status = 'Approved'
        elif action == 'deny':
            borrow_request.status = 'Denied'
        else:
            return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

        borrow_request.save()
        return Response({'message': f'Borrow request {action}d successfully.'})

# Library User: Get list of books
class BookListView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

# Library User: Submit a borrow request
class BorrowRequestView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BorrowRequestCreateSerializer(data=request.data)
        if serializer.is_valid():
            BorrowRequest.objects.create(
                user=request.user,
                book=serializer.validated_data['book'],
                date_from=serializer.validated_data['date_from'],
                date_to=serializer.validated_data['date_to'],
            )
            return Response({'message': 'Borrow request created successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Library User: View personal borrow history
    def get(self, request):
        borrow_requests = BorrowRequest.objects.filter(user=request.user)
        serializer = BorrowRequestSerializer(borrow_requests, many=True)
        return Response(serializer.data)

class UserBorrowHistoryView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if not request.user.is_librarian:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        borrow_requests = BorrowRequest.objects.filter(user=user)
        serializer = BorrowRequestSerializer(borrow_requests, many=True)
        return Response(serializer.data)


class DownloadBorrowHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch the borrow history for the logged-in user
        borrow_requests = BorrowRequest.objects.filter(user=request.user)

        # Create an HTTP response with the appropriate headers
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="borrow_history.csv"'

        # Create a CSV writer
        writer = csv.writer(response)

        # Write the header row
        writer.writerow(['Book Title', 'Date From', 'Date To', 'Status'])

        # Write data rows
        for borrow_request in borrow_requests:
            writer.writerow([
                borrow_request.book.title,
                borrow_request.date_from,
                borrow_request.date_to,
                borrow_request.status,
            ])

        return response