from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    CreateUserView, 
    BookListView, 
    BorrowRequestView, 
    LibrarianBorrowRequestView, 
    ManageBorrowRequestView,
    AddBookView, 
    UserBorrowHistoryView,
    UserListView,
    DownloadBorrowHistoryView
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('create-user/', CreateUserView.as_view(), name='create_user'),
    path('all-users/', UserListView.as_view(), name='all_user' ),
    # Librarian APIs
    path('librarian/add-book/', AddBookView.as_view(), name='add_book'),
    path('librarian/borrow-requests/', LibrarianBorrowRequestView.as_view(), name='librarian_borrow_requests'),
    path('librarian/borrow-request/<int:request_id>/', ManageBorrowRequestView.as_view(), name='manage_borrow_request'),
    path('librarian/user-borrow-history/<int:user_id>/', UserBorrowHistoryView.as_view(), name='user_borrow_history'),
    # User APIs
    path('user/books/', BookListView.as_view(), name='book_list'),
    path('user/borrow-requests/', BorrowRequestView.as_view(), name='borrow_requests'),

    path('user/download-borrow-history/', DownloadBorrowHistoryView.as_view(), name='download_borrow_history'),
]
