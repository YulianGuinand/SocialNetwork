from django.shortcuts import render, redirect
from django.db.models import Q
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpRequest
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from .models import Post, Comment, UserProfile
from .forms import PostForm, CommentForm
from django.views.generic.edit import UpdateView, DeleteView
from django.utils.html import linebreaks


class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all().order_by('-created_on')
        form = PostForm()

        post_data = []
        for post in posts:
            post.body = linebreaks(post.body)
            post_data.append([post.is_followed_by(request.user), post])

        context = {
            'post_list': posts,
            'form': form,
            'post_data': post_data,
        }

        return render(request, 'social/post_list.html', context)

    def post(self, request, *args, **kwargs):
        logged_user = request.user
        posts = Post.objects.all().order_by('-created_on')
        form = PostForm(request.POST)

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()

        context = {
            'post_list': posts,
            'form': form,
            'user': logged_user,
        }
        return render(request, 'social/post_list.html', context)

class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()
        comments = Comment.objects.filter(post=post).order_by('-created_on')
        post.body = linebreaks(post.body)
        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }

        return render(request, 'social/post_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
        
        comments = Comment.objects.filter(post=post).order_by('-created_on')

        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }

        return render(request, 'social/post_detail.html', context)

class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['body']
    template_name = 'social/post_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'social/post_delete.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'social/comment_delete.html'

    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

class ProfileView(View):
    
    def get(self, request, pk,*args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(author=user).order_by('-created_on')
        followers = profile.followers.all()
        
        profile.bio = linebreaks(profile.bio)
        
        number_of_followers = len(followers)
        if number_of_followers == 0:
            is_following = False
            
        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False
        
        number_of_posts = len(posts)
            
        context = {
            'user': user,
            'profile': profile,
            'number_of_posts': number_of_posts,
            'posts': posts,
            'number_of_followers': number_of_followers,
            'is_following': is_following,
        }
        
        return render(request, 'social/profile.html', context)
    
class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    fields = ['name', 'bio', 'birth_date', 'location', 'picture']
    template_name = 'social/profile_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk': pk})
    
    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user

class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk,*args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)
    
        return redirect('profile', pk=profile.pk)
    
class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)
        
        return redirect('profile', pk=profile.pk)
    
class AddFollowerPost(LoginRequiredMixin, View):
    def post(self, request, pk,*args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)
    
        return redirect('post-list')
    
class RemoveFollowerPost(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)
        
        return redirect('post-list')

class AddFollowerList(LoginRequiredMixin, View):
    def post(self, request, pk, pk_page,*args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)
    
        return redirect('list-followers', pk=pk_page)
    
class RemoveFollowerList(LoginRequiredMixin, View):
    def post(self, request, pk, pk_page,*args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)
        
        return redirect('list-followers', pk=pk_page)

class AddLike(LoginRequiredMixin, View):
    def post(self, request, pk,*args, **kwargs):
        post = Post.objects.get(pk=pk)
        
        is_dislike = False
        
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        
        if is_dislike:
            post.dislikes.remove(request.user)
        
        is_likes = False
        
        for like in post.likes.all():
            if like == request.user:
                is_likes = True
                break
            
        if not is_likes:
            post.likes.add(request.user)
        if is_likes:
            post.likes.remove(request.user)    
        
        next = request.POST.get('next', '/')
        
        return HttpResponseRedirect(next)

class AddDisLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        
        is_likes = False
        
        for like in post.likes.all():
            if like == request.user:
                is_likes = True
                break
        
        if is_likes:
            post.likes.remove(request.user)
        
        is_dislike = False
        
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        
        if not is_dislike:
            post.dislikes.add(request.user)
        if is_dislike:
            post.dislikes.remove(request.user)
        
        next = request.POST.get('next', '/')
        
        return HttpResponseRedirect(next)
        
class UserSearch(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        profile_list = UserProfile.objects.filter(
            Q(user__username__icontains=query)
        )
        
        context = {
            'profile_list': profile_list,
        }
        
        return render(request, 'social/search.html', context)
    
class ListFollowers(View):
    def get(self, request, pk, *args, **kwargs):
        profile  = UserProfile.objects.get(pk=pk)
        followers = profile.followers.all()
        
        followers_info = []
        
        for follower in followers:
            if request.user in follower.profile.followers.all():
                followers_info.append([True, follower])
            else:
                followers_info.append([False, follower])
                
        
        context = {
            'profile': profile,
            'followers': followers,
            'followers_info': followers_info,
        }
        
        return render(request, 'social/followers_list.html/', context)
    