from django.urls import path
from .views import PostListView, PostDetailView, PostEditView, PostDeleteView, CommentDeleteView, ProfileView, ProfileEditView, AddFollower, RemoveFollower
from .views import AddLike, AddDisLike, UserSearch, AddFollowerPost, RemoveFollowerPost, ListFollowers, AddFollowerList, RemoveFollowerList
urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/edit/<int:pk>/', PostEditView.as_view(), name='post-edit'),
    path('post/delete/<int:pk>/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:post_pk>/comment/delete/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('post/<int:pk>/like/', AddLike.as_view(), name="like"),
    path('post/<int:pk>/dislike/', AddDisLike.as_view(), name="dislike"),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/edit/<int:pk>/', ProfileEditView.as_view(), name='profile-edit'),
    path('profile/<int:pk>/followers/', ListFollowers.as_view(), name='list-followers'),
    path('profile/<int:pk>/followers/add/', AddFollower.as_view(), name='add-follower'),
    path('profile/<int:pk>/followers/remove/', RemoveFollower.as_view(), name='remove-follower'),
    path('profile/<int:pk>/followers/add-post/', AddFollowerPost.as_view(), name='add-follower-post'),
    path('profile/<int:pk>/followers/remove-post/', RemoveFollowerPost.as_view(), name='remove-follower-post'),
    path('profile/<int:pk>/followers/add-list/<int:pk_page>/', AddFollowerList.as_view(), name='add-follower-list'),
    path('profile/<int:pk>/followers/remove-list/<int:pk_page>/', RemoveFollowerList.as_view(), name='remove-follower-list'),
    path('search/', UserSearch.as_view(), name='profile-search'),
]
