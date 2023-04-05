from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View, TemplateView, CreateView, UpdateView,DeleteView
from biznews.models import Post, Category, Tag
from django.db.models import Q
from biznews.forms import NewsLetterForm, ContactForm, CommentForm, PostForm, CategoryForm, TagForm
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

class HomeView(ListView):
    model = Post
    template_name = "biznew/home.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(
        status = "published", published_at__isnull=False
    ).order_by("-published_at")[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_post"] = (
            Post.objects.filter(status = "published", published_at__isnull=False)
            .order_by("-views_count")
            .first()
        )
        context ["most_viewed_posts"] = Post.objects.filter(
                status = "published", published_at__isnull=False
            ).order_by("-views_count") [:5]
        context ["latest_posts"] = Post.objects.filter(
                status = "published", published_at__isnull=False
            ).order_by("-views_count") [:4]
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = "biznew/detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        obj = self.get_object()
        obj.views_count += 1
        obj.save()
        
        context["recent_posts"] = Post.objects.filter(
            status = "published", published_at__isnull=False
        ).order_by("-published_at") [:5]

        context["recent_posts"] = Post.objects.filter(
            status = "published", published_at__isnull=False
        ).order_by("-published_at") [:5]

        return context


class PostListView(ListView):
    model = Post
    template_name = "biznew/list.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(
        status = "published", published_at__isnull=False
    ).order_by("-published_at")    
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["most_viewed_posts"] = Post.objects.filter(
            status = "published", published_at__isnull=False
        ).order_by("-published_at") [:5]

        context["recent_posts"] = Post.objects.filter(
            status = "published", published_at__isnull=False
        ).order_by("-published_at") [:5]
     
        return context

class PostSearchView(View):
    def get(self, request, *args, **kwargs):
        print(request.GET)
        query = request.GET["query"]
        posts = Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
        
        return render(request,"biznew/list.html",{"query":query, "posts":posts},)
    
class NewsLetterView(View):
    form_class = NewsLetterForm

    def post (self, request, *args, **kwargs):
        is_ajax = request.headers.get("x-requested-with")
        print(is_ajax)
        if is_ajax == 'XMLHttpRequest':
            form = self.form_class(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Successfully submitted your email address. We will contact you soon",
                    },
                    status=200,
                    )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Something went wrong. Please make sure your form is correct.",
                    },
                    status=400,
                )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Cannot process. Must be an ajax request.",
                },
                status=400,
            )
        
class PostByCategory(ListView):
    model = Post
    template_name = "biznew/list.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["recent_posts"] = Post.objects.filter(
            status = "published", published_at__isnull=False
        ).order_by("-published_at") [:5]

        return context
    
    def get_queryset(self):
        super().get_queryset()
        queryset = Post.objects.filter(
            status = "published", 
            published_at__isnull=False, 
            category=self.kwargs["cat_id"]
        )
        return queryset
    
class PostByTag(ListView):
    model = Post
    template_name = "biznew/list.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["recent_posts"] = Post.objects.filter(
            status = "published", published_at__isnull=False
        ).order_by("-published_at") [:5]

        return context

    def get_queryset(self):
        super().get_queryset()
        queryset = Post.objects.filter(
            status = "published", 
            published_at__isnull=False, 
            tag=self.kwargs["tag_id"]
        )
        return queryset    
    
class ContactView(View):
    template_name = "biznew/contact.html"
    form_class = ContactForm

    def get(self, request, *args, **kwargs):
        return render (request, self.template_name)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Successfully submitted your message. We will contact you soon.",)
        else:
            messages.error(request, "Cannot submit your message. Something went wrong.",)    
        return render (request, self.template_name, {"form": form})
    
class CommentView(View):
    form_class = CommentForm
    template_name = "biznew/detail.html"

    def post(self, request, *args, **kwargs):
        post_id = request.POST['post']

        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post-detail', post_id)
        else:
            post = Post.objects.get(id=post_id)
            return render(request, self.template_name, {"post": post, "form": form},)


class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "news_admin/post_list.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(published_at__isnull=True).order_by("-published_at")

class PostPublishView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        post.published_at = timezone.now()
        post.save()
        return redirect("post-list")

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "news_admin/post_create.html"
    success_url = reverse_lazy("draft-list")

    def form_valid(self, form):
        # make logged-in user as a author of the post
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        post.delete()
        return redirect("post-list")


class PostUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        form = PostForm(instance=post)
        return render(
            request,
            "news_admin/post_create.html",
            {"form": form},
        )

    def post(self, request, pk):
        post = Post.objects.get(pk=pk)
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            form.save()
            return redirect("post-list")

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "news_admin/category_create.html"
    success_url = reverse_lazy("draft-list")

    def form_valid(self, form):
        # make logged-in user as a author of the post
        form.instance.author = self.request.user
        return super().form_valid(form)

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "news_admin/category_list.html"
    context_object_name = "categories"
            
class CategoryDetailView(DetailView):
    model = Category
    template_name = "news_admin/category_detail.html"
    context_object_name = "category"

class CategoryDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return redirect("category-list")


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "news_admin/category_create.html"
    success_url = reverse_lazy("home")
   
class TagCreateView(LoginRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = "news_admin/tag_create.html"
    success_url = reverse_lazy("draft-list")

class TagDetailView(DetailView):
    model = Tag
    template_name = "news_admin/tag_detail.html"
    context_object_name = "tag"


class TagListView(LoginRequiredMixin, ListView):
    model = Tag
    template_name = "news_admin/tag_list.html"
    context_object_name = "tags"


class TagDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        tag = get_object_or_404(Tag, pk=pk)
        tag.delete()
        return redirect("tag-list")


class TagUpdateView(LoginRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = "news_admin/tag_create.html"
    success_url = reverse_lazy("home")       