"""Seed database with initial categories and sample content"""

from django.core.management.base import BaseCommand
from forum.models import Category
from knowledge.models import ArticleCategory


class Command(BaseCommand):
    help = 'Seeds the database with initial categories'

    def handle(self, *args, **options):

        # Forum Categories
        forum_categories = [
            {
                'name': 'Crops & Cultivation',
                'slug': 'crops-cultivation',
                'description': 'Maize, tobacco, vegetables, soil preparation, irrigation and crop management.',
                'order': 1,
            },
            {
                'name': 'Livestock & Poultry',
                'slug': 'livestock-poultry',
                'description': 'Cattle, goats, chickens, pigs, animal nutrition and breeding.',
                'order': 2,
            },
            {
                'name': 'Pests & Diseases',
                'slug': 'pests-diseases',
                'description': 'Crop diseases, animal diseases, pest identification and control methods.',
                'order': 3,
            },
            {
                'name': 'Markets & Selling',
                'slug': 'markets-selling',
                'description': 'Pricing, finding buyers, market access, value addition and agribusiness.',
                'order': 4,
            },
            {
                'name': 'Equipment & Technology',
                'slug': 'equipment-technology',
                'description': 'Tractors, irrigation systems, drones, farming apps and modern tools.',
                'order': 5,
            },
            {
                'name': 'Weather & Climate',
                'slug': 'weather-climate',
                'description': 'Seasonal planning, drought management, rainfall patterns and climate adaptation.',
                'order': 6,
            },
            {
                'name': 'Funding & Grants',
                'slug': 'funding-grants',
                'description': 'Agricultural loans, government programs, NGO support and financial planning.',
                'order': 7,
            },
            {
                'name': 'General Discussion',
                'slug': 'general-discussion',
                'description': 'Introductions, farming life, success stories and community chat.',
                'order': 8,
            },
        ]

        # Knowledge Base Categories
        knowledge_categories = [
            {
                'name': 'Crop Farming',
                'slug': 'crop-farming',
                'description': 'Guides on growing maize, tobacco, groundnuts, vegetables and more.',
                'order': 1,
            },
            {
                'name': 'Animal Husbandry',
                'slug': 'animal-husbandry',
                'description': 'Raising cattle, goats, poultry and managing animal health.',
                'order': 2,
            },
            {
                'name': 'Soil & Water',
                'slug': 'soil-water',
                'description': 'Soil testing, composting, irrigation methods and water conservation.',
                'order': 3,
            },
            {
                'name': 'Pest Management',
                'slug': 'pest-management',
                'description': 'Identifying and controlling pests and diseases in crops and livestock.',
                'order': 4,
            },
            {
                'name': 'Agribusiness',
                'slug': 'agribusiness',
                'description': 'Marketing, pricing, record keeping and growing your farm business.',
                'order': 5,
            },
            {
                'name': 'Climate Smart Farming',
                'slug': 'climate-smart-farming',
                'description': 'Adapting to climate change, drought-resistant crops and conservation farming.',
                'order': 6,
            },
        ]

        # Seed Forum Categories
        created_forum = 0
        for cat_data in forum_categories:
            obj, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                created_forum += 1

        # Seed Knowledge Categories
        created_knowledge = 0
        for cat_data in knowledge_categories:
            obj, created = ArticleCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                created_knowledge += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {created_forum} forum categories and {created_knowledge} knowledge categories.'
        ))