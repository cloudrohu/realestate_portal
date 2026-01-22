from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Category, Tag, Comment, Blog
from .forms import PostForm, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q, F
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import models as djmodels 
from home.models import Setting


def index(request):
    settings_obj = Setting.objects.first()
    cities = City.objects.filter(level_type="CITY").order_by("name")

    residential_type = PropertyType.objects.filter(name__iexact="Residential", is_top_level=True).first()
    commercial_type = PropertyType.objects.filter(name__iexact="Commercial", is_top_level=True).first()

    residential_types = residential_type.get_descendants(include_self=True) if residential_type else PropertyType.objects.none()
    commercial_types = commercial_type.get_descendants(include_self=True) if commercial_type else PropertyType.objects.none()

    new_launch_residential = Project.objects.filter(
        active=True, construction_status__iexact="New Launch", propert_type__in=residential_types
    ).select_related("city", "locality", "developer", "propert_type").prefetch_related("configurations").order_by("-create_at")[:10]

    new_launch_commercial = Project.objects.filter(
        active=True, construction_status__iexact="New Launch", propert_type__in=commercial_types
    ).select_related("city", "locality", "developer", "propert_type").prefetch_related("configurations").order_by("-create_at")[:10]

    project_featured = Project.objects.filter(
        active=True, featured_property=True
    ).select_related("city", "locality", "developer", "propert_type").prefetch_related("configurations").order_by("-create_at")[:6]

    featured_developers = Developer.objects.filter(featured_builder=True).order_by("-create_at")[:8]
    featured_locality = Locality.objects.filter(featured_locality=True).order_by("name")[:20]
    bank = Bank.objects.filter(home_loan_partner=True).order_by("title")
    blogs = Blog.objects.filter(is_published=True).order_by("-published_date", "-created_at")[:3]


    about_page = About.objects.filter(is_active=True).first()
    about_page = About.objects.filter(is_active=True).first()
    impactmetric = ImpactMetric.objects.all()
    amenities = ProjectAmenities.objects.all()
    why_choose_items = Why_Choose.objects.filter(is_active=True).order_by("order")
    testimonials = Testimonial.objects.all().order_by("-id")
    faqs = FAQ.objects.all().order_by("id")

    current_city = project_featured.first().city.name if project_featured.exists() else "Mumbai"

    return render(
        request,
        "home/index.html",
        {
            "settings_obj": settings_obj,
            "bank": bank,
            "cities": cities,
            "current_city": current_city,
            "impactmetric": impactmetric,
            "amenities": amenities,
            "project_featured": project_featured,
            "new_launch_residential": new_launch_residential,
            "new_launch_commercial": new_launch_commercial,
            "featured_developers": featured_developers,
            "featured_locality": featured_locality,
            "about_page": about_page,
            "why_choose_items": why_choose_items,
            "testimonials": testimonials,
            "faqs": faqs,
            "blogs": blogs,
        }
    )


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        qs = Post.objects.filter(status='published').order_by('-publish_date')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(excerpt__icontains=q) |
                Q(content__icontains=q) |
                Q(tags__name__icontains=q)
            ).distinct()
        cat = self.kwargs.get('category_slug')
        if cat:
            qs = qs.filter(category__slug=cat)
        tag = self.kwargs.get('tag_slug')
        if tag:
            qs = qs.filter(tags__slug=tag)
        return qs


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        obj = get_object_or_404(Post, slug=self.kwargs.get('slug'), status='published')
        # increment view count
        Post.objects.filter(pk=obj.pk).update(views=F('views') + 1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.filter(active=True)
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user or self.request.user.is_staff


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user or self.request.user.is_staff


@require_POST
def post_comment(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.active = False   # moderation
        comment.save()
    return redirect(post.get_absolute_url())

def blog_detail(request, slug):
    settings_obj = Setting.objects.first()
    blog = get_object_or_404(Blog, slug=slug, is_published=True)
    related_blogs = Blog.objects.filter(is_published=True, category=blog.category).exclude(id=blog.id).order_by("-published_date")[:3]

    context = {
        "settings_obj": settings_obj,
        "blog": blog,
        "related_blogs": related_blogs,
    }
    return render(request, "blog/blog_detail.html", context)

def blog_list(request):
    settings_obj = Setting.objects.first()

    blogs_qs = Blog.objects.filter(is_published=True).order_by("-published_date", "-created_at")

    q = request.GET.get("q")
    if q:
        blogs_qs = blogs_qs.filter(
            Q(title__icontains=q) |
            Q(short_description__icontains=q) |
            Q(content__icontains=q) |
            Q(author_name__icontains=q) |
            Q(category__name__icontains=q)
        ).distinct()

    paginator = Paginator(blogs_qs, 9)  # 9 per page (3x3 desktop)
    page_number = request.GET.get("page")
    blogs = paginator.get_page(page_number)

    context = {
        "settings_obj": settings_obj,
        "blogs": blogs,
        "q": q,
    }
    return render(request, "blog/blog_list.html", context)