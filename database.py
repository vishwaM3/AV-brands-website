"""
AV Brands - Database Initialization
Creates and populates the database with initial data
"""
import os
import json
from app import app, db
from models import User, Category, Product, Offer

def init_database():
    """Initialize the database with all tables and default data"""
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created")
        
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@avbrands.com').first()
        
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@avbrands.com',
                phone='+91 9876543210',
                address='123 Fashion Street',
                city='Bangalore',
                state='Karnataka',
                pincode='560001',
                is_admin=True
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            print("✓ Admin user created")
        
        # Create default categories
        categories_data = [
            {'name': 'Men', 'name_kannada': 'ಪುರುಷರು', 'slug': 'men', 'description': 'Men\'s clothing collection'},
            {'name': 'Women', 'name_kannada': 'ಮಹಿಳೆಯರು', 'slug': 'women', 'description': 'Women\'s clothing collection'},
            {'name': 'Kids', 'name_kannada': 'ಮಕ್ಕಳು', 'slug': 'kids', 'description': 'Kids clothing collection'},
            {'name': 'Accessories', 'name_kannada': 'ಪರಿಕರಗಳು', 'slug': 'accessories', 'description': 'Fashion accessories'},
            {'name': 'Footwear', 'name_kannada': 'ಬೂಟುಗಳು', 'slug': 'footwear', 'description': 'Shoes and sandals'}
        ]
        
        for cat_data in categories_data:
            existing_cat = Category.query.filter_by(slug=cat_data['slug']).first()
            if not existing_cat:
                category = Category(**cat_data)
                db.session.add(category)
        
        db.session.commit()
        print("✓ Categories created")
        
        # Create sample products
        men_cat = Category.query.filter_by(slug='men').first()
        women_cat = Category.query.filter_by(slug='women').first()
        kids_cat = Category.query.filter_by(slug='kids').first()
        
        if men_cat and Product.query.count() == 0:
            products = [
                {
                    'name': 'Premium Cotton Shirt',
                    'name_kannada': 'ಪ್ರೀಮಿಯಂ ಕಾಟನ್ ಶರಟ್',
                    'description': 'High-quality premium cotton shirt for men. Perfect for formal and casual occasions.',
                    'description_kannada': 'ಪುರುಷರಿಗಾಗಿ ಉನ್ನತ ಗುಣಮಟ್ಟದ ಪ್ರೀಮಿಯಂ ಕಾಟನ್ ಶರಟ್. ಔಪಚಾರಿಕ ಮತ್ತು ಕ್ಯಾಜುವಲ್ ಸಂದರ್ಭಗಳಿಗೆ ಪರಿಪೂರ್ಣ.',
                    'price': 1499.00,
                    'discount_price': 1199.00,
                    'category_id': men_cat.id,
                    'sizes': json.dumps(['S', 'M', 'L', 'XL', 'XXL']),
                    'colors': json.dumps(['White', 'Blue', 'Black']),
                    'stock': 50,
                    'is_featured': True,
                    'image1': 'product_men_1.jpg'
                },
                {
                    'name': 'Slim Fit Jeans',
                    'name_kannada': 'ಸ್ಲಿಮ್ ಫಿಟ್ ಜೀನ್ಸ್',
                    'description': 'Modern slim fit jeans with premium denim quality.',
                    'description_kannada': 'ಪ್ರೀಮಿಯಂ ಡೆನಿಮ್ ಗುಣಮಟ್ಟದ ಆಧುನಿಕ ಸ್ಲಿಮ್ ಫಿಟ್ ಜೀನ್ಸ್.',
                    'price': 2499.00,
                    'discount_price': 1999.00,
                    'category_id': men_cat.id,
                    'sizes': json.dumps(['28', '30', '32', '34', '36']),
                    'colors': json.dumps(['Blue', 'Black', 'Grey']),
                    'stock': 35,
                    'is_featured': True,
                    'image1': 'product_men_2.jpg'
                },
                {
                    'name': 'Classic Polo T-Shirt',
                    'name_kannada': 'ಕ್ಲಾಸಿಕ್ ಪೋಲೋ ಟೀ ಶರಟ್',
                    'description': 'Comfortable cotton polo t-shirt for everyday wear.',
                    'description_kannada': 'ದೈನಂದಿನ ಧರಿಸಲು ಆರಾಮದಾಯಕ ಕಾಟನ್ ಪೋಲೋ ಟೀ ಶರಟ್.',
                    'price': 899.00,
                    'category_id': men_cat.id,
                    'sizes': json.dumps(['S', 'M', 'L', 'XL']),
                    'colors': json.dumps(['Navy', 'Red', 'White', 'Green']),
                    'stock': 100,
                    'is_featured': True,
                    'image1': 'product_men_3.jpg'
                },
                {
                    'name': 'Formal Blazer',
                    'name_kannada': 'ಔಪಚಾರಿಕ ಬ್ಲೇಜರ್',
                    'description': 'Elegant formal blazer for professional look.',
                    'description_kannada': 'ವೃತ್ತಿಪರ ನೋಟಕ್ಕಾಗಿ ಸೊಬಗಿನ ಔಪಚಾರಿಕ ಬ್ಲೇಜರ್.',
                    'price': 4999.00,
                    'discount_price': 3999.00,
                    'category_id': men_cat.id,
                    'sizes': json.dumps(['S', 'M', 'L', 'XL', 'XXL']),
                    'colors': json.dumps(['Black', 'Navy', 'Grey']),
                    'stock': 20,
                    'image1': 'product_men_4.jpg'
                },
                {
                    'name': 'Casual Hoodie',
                    'name_kannada': 'ಕ್ಯಾಜುವಲ್ ಹುಡೀ',
                    'description': 'Warm and stylish hoodie for casual outings.',
                    'description_kannada': 'ಕ್ಯಾಜುವಲ್ ಹೋಗುವ ಸಂದರ್ಭಗಳಿಗೆ ಬೆಚ್ಚಗಿನ ಮತ್ತು ಸ್ಟೈಲಿಶ್ ಹುಡೀ.',
                    'price': 1799.00,
                    'category_id': men_cat.id,
                    'sizes': json.dumps(['S', 'M', 'L', 'XL', 'XXL']),
                    'colors': json.dumps(['Black', 'Grey', 'Blue']),
                    'stock': 45,
                    'image1': 'product_men_5.jpg'
                }
            ]
            
            for product_data in products:
                product = Product(**product_data)
                db.session.add(product)
            
            print("✓ Men's products created")
        
        if women_cat and Product.query.count() < 6:
            products = [
                {
                    'name': 'Elegant Saree',
                    'name_kannada': 'ಸೊಬಗಿನ ಸೀರೆ',
                    'description': 'Beautiful traditional silk saree with intricate designs.',
                    'description_kannada': 'ಸಂಕೀರ್ಣ ವಿನ್ಯಾಸಗಳೊಂದಿಗೆ ಸುಂದರವಾದ ಸಾಂಪ್ರದಾಯಿಕ ರೇಷ್ಮೆ ಸೀರೆ.',
                    'price': 3999.00,
                    'discount_price': 2999.00,
                    'category_id': women_cat.id,
                    'sizes': json.dumps(['Free Size']),
                    'colors': json.dumps(['Red', 'Blue', 'Maroon', 'Green']),
                    'stock': 25,
                    'is_featured': True,
                    'image1': 'product_women_1.jpg'
                },
                {
                    'name': 'Designer Kurti',
                    'name_kannada': 'ಡಿಸೈನರ್ ಕುರ್ತಿ',
                    'description': 'Modern designer kurti with beautiful embroidery.',
                    'description_kannada': 'ಸುಂದರವಾದ ಕಸೂತಿ ಕೆಲಸದೊಂದಿಗೆ ಆಧುನಿಕ ಡಿಸೈನರ್ ಕುರ್ತಿ.',
                    'price': 1899.00,
                    'discount_price': 1499.00,
                    'category_id': women_cat.id,
                    'sizes': json.dumps(['S', 'M', 'L', 'XL']),
                    'colors': json.dumps(['Pink', 'Orange', 'Blue', 'Yellow']),
                    'stock': 40,
                    'is_featured': True,
                    'image1': 'product_women_2.jpg'
                },
                {
                    'name': 'Casual Jeans',
                    'name_kannada': 'ಕ್ಯಾಜುವಲ್ ಜೀನ್ಸ್',
                    'description': 'Comfortable casual jeans for women.',
                    'description_kannada': 'ಮಹಿಳೆಯರಿಗಾಗಿ ಆರಾಮದಾಯಕ ಕ್ಯಾಜುವಲ್ ಜೀನ್ಸ್.',
                    'price': 1599.00,
                    'category_id': women_cat.id,
                    'sizes': json.dumps(['26', '28', '30', '32', '34']),
                    'colors': json.dumps(['Blue', 'Black', 'Light Blue']),
                    'stock': 50,
                    'is_featured': True,
                    'image1': 'product_women_3.jpg'
                },
                {
                    'name': 'Floral Dress',
                    'name_kannada': 'ಹೂವಿನ ಡ್ರೆಸ್',
                    'description': 'Beautiful floral print dress for parties.',
                    'description_kannada': 'ಪಾರ್ಟಿಗಳಿಗಾಗಿ ಸುಂದರವಾದ ಹೂವಿನ ಪ್ರಿಂಟ್ ಡ್ರೆಸ್.',
                    'price': 2299.00,
                    'discount_price': 1799.00,
                    'category_id': women_cat.id,
                    'sizes': json.dumps(['S', 'M', 'L', 'XL']),
                    'colors': json.dumps(['Floral Pink', 'Floral Blue']),
                    'stock': 30,
                    'image1': 'product_women_4.jpg'
                },
                {
                    'name': 'Western Top',
                    'name_kannada': 'ವೆಸ್ಟರ್ನ್ ಟಾಪ್',
                    'description': 'Trendy western top for modern women.',
                    'description_kannada': 'ಆಧುನಿಕ ಮಹಿಳೆಯರಿಗಾಗಿ ಟ್ರೆಂಡಿ ವೆಸ್ಟರ್ನ್ ಟಾಪ್.',
                    'price': 999.00,
                    'category_id': women_cat.id,
                    'sizes': json.dumps(['S', 'M', 'L', 'XL']),
                    'colors': json.dumps(['White', 'Black', 'Red']),
                    'stock': 60,
                    'image1': 'product_women_5.jpg'
                }
            ]
            
            for product_data in products:
                product = Product(**product_data)
                db.session.add(product)
            
            print("✓ Women's products created")
        
        if kids_cat and Product.query.count() < 12:
            products = [
                {
                    'name': 'Kids T-Shirt Set',
                    'name_kannada': 'ಮಕ್ಕಳ ಟೀ ಶರಟ್ ಸೆಟ್',
                    'description': 'Set of 3 colorful t-shirts for kids.',
                    'description_kannada': 'ಮಕ್ಕಳಿಗಾಗಿ 3 ಬಣ್ಣಬಣ್ಣದ ಟೀ ಶರಟ್ ಗಳ ಸೆಟ್.',
                    'price': 799.00,
                    'discount_price': 599.00,
                    'category_id': kids_cat.id,
                    'sizes': json.dumps(['2-3Y', '3-4Y', '4-5Y', '5-6Y']),
                    'colors': json.dumps(['Multicolor']),
                    'stock': 40,
                    'is_featured': True,
                    'image1': 'product_kids_1.jpg'
                },
                {
                    'name': 'Kids Frock',
                    'name_kannada': 'ಮಕ್ಕಳ ಫ್ರಾಕ್',
                    'description': 'Cute frock for little girls.',
                    'description_kannada': 'ಚಿಕ್ಕ ಹುಡಿಯರಿಗಾಗಿ ತುಂಬಾ ಸ್ಟೈಲಿಶ್ ಫ್ರಾಕ್.',
                    'price': 1199.00,
                    'discount_price': 899.00,
                    'category_id': kids_cat.id,
                    'sizes': json.dumps(['2-3Y', '3-4Y', '4-5Y', '5-6Y', '6-7Y']),
                    'colors': json.dumps(['Pink', 'Yellow', 'White']),
                    'stock': 25,
                    'image1': 'product_kids_2.jpg'
                },
                {
                    'name': 'Kids Shorts',
                    'name_kannada': 'ಮಕ್ಕಳ ಶಾರ್ಟ್ಸ್',
                    'description': 'Comfortable shorts for boys.',
                    'description_kannada': 'ಹುಡುಗರಿಗಾಗಿ ಆರಾಮದಾಯಕ ಶಾರ್ಟ್ಸ್.',
                    'price': 599.00,
                    'category_id': kids_cat.id,
                    'sizes': json.dumps(['2-3Y', '3-4Y', '4-5Y', '5-6Y']),
                    'colors': json.dumps(['Blue', 'Khaki', 'Grey']),
                    'stock': 35,
                    'image1': 'product_kids_3.jpg'
                }
            ]
            
            for product_data in products:
                product = Product(**product_data)
                db.session.add(product)
            
            print("✓ Kids products created")
        
        # Create sample offer
        if Offer.query.count() == 0:
            featured_product = Product.query.filter_by(is_featured=True).first()
            if featured_product:
                offer = Offer(
                    title='Flat 30% Off on All Featured Items!',
                    title_kannada='ಎಲ್ಲಾ ವಿಶೇಷ ಐಟಂಗಳ ಮೇಲೆ 30% ರಿಯಾಯಿತಿ!',
                    description='Get amazing discounts on all featured products. Limited time offer!',
                    description_kannada='ಎಲ್ಲಾ ವಿಶೇಷ ಉತ್ಪನ್ನಗಳ ಮೇಲೆ ಅದ್ಭುತ ರಿಯಾಯಿತಿಗಳನ್ನು ಪಡೆಯಿರಿ. ಸೀಮಿತ ಸಮಯದ ಆಫರ್!',
                    discount_percentage=30.0,
                    product_id=featured_product.id,
                    is_active=True
                )
                db.session.add(offer)
                print("✓ Sample offer created")
        
        db.session.commit()
        print("\n✅ Database initialization complete!")
        print("\n📋 Login Credentials:")
        print("   Admin: admin@avbrands.com / Admin@123")
        print("   Customer: Register at /signup")


if __name__ == '__main__':
    init_database()

