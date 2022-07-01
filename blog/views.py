from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.shortcuts import redirect


def home(request):
    return render(request, 'blog/home.html')


def sign_up(request):
    if request.method == "POST":
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if User.objects.filter(username=username):
            messages.error(request,"Username already exists.:Try some other username.")
            return redirect('home')
        if User.objects.filter(email=email):
            messages.error(request,"email already registered.:Try some other email.")
            return redirect('home')
        if password != confirm_password:
            messages.error(request, "Password mismatched!")
            return redirect('home')
        my_user = User.objects.create_user(username, email, password)
        my_user.first_name = first_name
        my_user.last_name = last_name
        my_user.save()
        messages.success(request, "Your account has been successfully created.")
        return redirect('sign_in')
    else:
        return render(request, 'blog/sign_up.html')


def sign_in(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('post_list')
        else:
            messages.error(request, "Bad Credentials.")
            return redirect('home')
    return render(request, 'blog/sign_in.html')


def sign_out(request):
    logout(request)
    messages.success(request,"You have sucessfully logged out.")
    return redirect('home')


def post_list(request):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    posts = Post.objects.order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post_id=pk)
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments})


def post_new(request):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        messages.error(request, "You cannot edit this post.")
        return redirect('post_detail', pk=post.pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


def add_comment(request, pk):
    if not request.user.is_authenticated:
        return redirect('home')
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment.html', {'form': form})


def add_like(request, comment_id):
    if not request.user.is_authenticated:
        return redirect('sign_in')
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == "POST":
        comment.like += 1
        comment.save()
    return redirect('post_detail', pk=comment.post.id)
