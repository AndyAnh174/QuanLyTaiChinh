"""
Management command to initialize default categories
"""
from django.core.management.base import BaseCommand
from app.models import Category


DEFAULT_CATEGORIES = [
    # Chi tiêu hàng ngày
    {"name": "Ăn uống", "icon": "🍜", "description": "Chi tiêu ăn uống, nhà hàng, cafe"},
    {"name": "Di chuyển", "icon": "🚗", "description": "Xăng xe, grab, taxi, xe buýt"},
    {"name": "Mua sắm", "icon": "🛒", "description": "Quần áo, đồ dùng cá nhân"},
    {"name": "Giải trí", "icon": "🎮", "description": "Xem phim, game, du lịch"},
    {"name": "Sức khỏe", "icon": "💊", "description": "Thuốc, khám bệnh, gym"},
    {"name": "Giáo dục", "icon": "📚", "description": "Học phí, sách vở, khóa học"},
    
    # Chi phí cố định
    {"name": "Nhà ở", "icon": "🏠", "description": "Tiền thuê nhà, điện nước"},
    {"name": "Điện thoại/Internet", "icon": "📱", "description": "Cước điện thoại, wifi"},
    {"name": "Bảo hiểm", "icon": "🛡️", "description": "Bảo hiểm y tế, xe, nhân thọ"},
    
    # Thu nhập
    {"name": "Lương", "icon": "💰", "description": "Lương tháng, thưởng"},
    {"name": "Freelance", "icon": "💻", "description": "Thu nhập từ công việc tự do"},
    {"name": "Đầu tư", "icon": "📈", "description": "Lãi đầu tư, cổ tức"},
    {"name": "Quà tặng", "icon": "🎁", "description": "Tiền mừng, quà tặng"},
    
    # Khác
    {"name": "Nợ/Vay", "icon": "💳", "description": "Cho vay, đi vay, trả nợ"},
    {"name": "Khác", "icon": "📦", "description": "Chi tiêu không phân loại"},
]


class Command(BaseCommand):
    help = 'Initialize default categories for the finance app'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force create categories even if they already exist',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        created_count = 0
        skipped_count = 0

        for cat_data in DEFAULT_CATEGORIES:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'icon': cat_data['icon'],
                    'description': cat_data['description'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Created category: {cat_data['icon']} {cat_data['name']}")
                )
            else:
                skipped_count += 1
                if force:
                    # Update existing category
                    category.icon = cat_data['icon']
                    category.description = cat_data['description']
                    category.save()
                    self.stdout.write(
                        self.style.WARNING(f"🔄 Updated category: {cat_data['icon']} {cat_data['name']}")
                    )
                else:
                    self.stdout.write(
                        self.style.NOTICE(f"⏭️ Skipped (exists): {cat_data['name']}")
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n📊 Summary: Created {created_count}, Skipped {skipped_count}"
            )
        )
