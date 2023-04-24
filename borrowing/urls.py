from django.urls import path

from borrowing.views import BorrowingListView, BorrowingDetailView

urlpatterns = [
    path("/borrowings/", BorrowingListView.as_view(), name="borrowing-list"),
    path(
        "/borrowings/<int:id>/",
        BorrowingDetailView.as_view(),
        name="borrowing-detail"
    ),
]

app_name = "borrowing"
