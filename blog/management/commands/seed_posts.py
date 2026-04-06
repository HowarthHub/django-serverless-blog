from django.core.management.base import BaseCommand

from blog.models import Post


class Command(BaseCommand):
    help = "Seed the database with sample blog posts"

    def handle(self, *args, **options):
        posts = [
            {
                "title": "Getting Started with Django REST Framework",
                "slug": "getting-started-with-drf",
                "content": "Django REST Framework makes it easy to build powerful APIs. In this post we walk through setting up serializers, viewsets, and routers to get a fully functional REST API running in minutes.",
                "status": Post.Status.PUBLISHED,
            },
            {
                "title": "The Repository Pattern in Python",
                "slug": "repository-pattern-python",
                "content": "Separating data access from business logic keeps your codebase clean and testable. We explore how to implement the repository pattern using abstract base classes and generics in Python.",
                "status": Post.Status.PUBLISHED,
            },
            {
                "title": "Deploying Django on AWS Lambda",
                "slug": "deploying-django-aws-lambda",
                "content": "Serverless Django is surprisingly straightforward with Mangum. This draft covers packaging your app, configuring API Gateway, and handling static files in a Lambda environment.",
                "status": Post.Status.DRAFT,
            },
        ]

        for data in posts:
            post, created = Post.objects.get_or_create(
                slug=data["slug"],
                defaults=data,
            )
            status = "Created" if created else "Already exists"
            self.stdout.write(f"  {status}: {post.title}")

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
