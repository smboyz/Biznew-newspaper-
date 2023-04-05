import csv
import io

from django.contrib.auth import get_user_model
from django.http import FileResponse, HttpResponse
from django.utils.html import strip_tags
from django.utils.text import slugify
from django.views.generic import View
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from biznews.models import Post

User = get_user_model()

COLUMNS = [
    "first_name",
    "last_name",
    "username",
    "email",
    "is_staff",
    "is_active",
    "is_superuser",
    "last_login",
    "date_joined",
]


class UserReportView(View):
    def get(self, request):

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=users.csv"

        users = User.objects.all().only(*COLUMNS).values(*COLUMNS)
        print(users)

        writer = csv.DictWriter(response, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)

        return response


class PDFFileDownloadView(View):
    def generate_styles(self):
        styles = getSampleStyleSheet()

        title = ParagraphStyle(
            "post_title",
            fontName="Helvetica-Bold",
            fontSize=16,
            parent=styles["Heading2"],
            alignment=1,
            spaceAfter=14,
        )
        content = ParagraphStyle(
            name="Justify",
            alignment=TA_JUSTIFY,
        )
        styles.add(content)
        styles.add(title)
        return styles

    def get(self, request):

        canvas = []
        buffer = io.BytesIO()
        styles = self.generate_styles()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        post = Post.objects.filter(status="published").order_by("-created_at").first()

        # post title
        canvas.append(Paragraph(post.title, styles["post_title"]))
        canvas.append(Spacer(1, 12))

        # post content
        content = strip_tags(post.content)
        canvas.append(Paragraph(content, styles["Justify"]))
        canvas.append(Spacer(1, 12))

        doc.build(canvas)

        buffer.seek(0)

        return FileResponse(
            buffer, as_attachment=True, filename=f"{slugify(post.title)}.pdf"
        )


import tempfile

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML


class PostDownloadView(View):
    def get(self, request, *args, **kwargs):
        # queryset
        posts = Post.objects.all()

        # context passed in the template
        context = {"posts": posts}

        # render
        html_string = render_to_string("reports/posts.html", context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        result = html.write_pdf()

        # http response
        response = HttpResponse(content_type="application/pdf;")
        response["Content-Disposition"] = "inline; filename=posts.pdf"
        response["Content-Transfer-Encoding"] = "binary"

        with tempfile.NamedTemporaryFile(delete=True) as output:
            output.write(result)
            output.flush()
            output = open(output.name, "rb")
            response.write(output.read())

        return response
