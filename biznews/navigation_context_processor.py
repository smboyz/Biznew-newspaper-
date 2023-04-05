from biznews.models import Category, Tag, Post
from django.db.models import F, Sum

def navigation(request):
    categories = Category.objects.all()
    top_categories = (
        Post.objects.values("category__pk","category__name")
        .annotate(
            pk=F("category__pk"), name=F("category__name"), max_views=Sum("views_count")
        )
        .order_by("-views_count")
        .values("pk", "name", "max_views")
    )[:4]
    print(top_categories)
    tags = Tag.objects.all()[:10]
    return {
        "categories" : categories,
        "top_categories": top_categories,
        "tags" : tags,
    }