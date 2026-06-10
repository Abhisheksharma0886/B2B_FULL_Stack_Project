from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import UserProfile, Product, Order

class SCMWorkflowTests(TestCase):
    def get_dummy_image(self):
        return SimpleUploadedFile(
            name='test.gif',
            content=b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
            content_type='image/gif'
        )

    def setUp(self):
        self.client = Client()

        # Create roles
        self.buyer_pwd = 'buyerpassword'
        self.buyer = UserProfile.objects.create_user(
            username='buyer1',
            email='buyer@test.com',
            password=self.buyer_pwd,
            role='buyer',
            profile_picture=self.get_dummy_image()
        )

        self.vendor_pwd = 'vendorpassword'
        self.vendor = UserProfile.objects.create_user(
            username='vendor1',
            email='vendor@test.com',
            password=self.vendor_pwd,
            role='vendor',
            profile_picture=self.get_dummy_image()
        )

        self.shipper = UserProfile.objects.create_user(
            username='shipper1',
            email='shipper@test.com',
            password='shipperpassword',
            role='shipper',
            profile_picture=self.get_dummy_image()
        )

        self.ofd_agent = UserProfile.objects.create_user(
            username='ofd1',
            email='ofd@test.com',
            password='ofdpassword',
            role='out_for_delivery',
            profile_picture=self.get_dummy_image()
        )

        self.delivered_agent = UserProfile.objects.create_user(
            username='delivered1',
            email='delivered@test.com',
            password='deliveredpassword',
            role='delivered',
            profile_picture=self.get_dummy_image()
        )

        # Create product
        self.product = Product.objects.create(
            vendor=self.vendor,
            name='Industrial Steel Bolts',
            description='High tensile structural steel bolts',
            price=150.00,
            available_quantity=100,
            offer_percentage=10.00, # 10% off -> discounted_price = 135.00
            image1=self.get_dummy_image()
        )

    def test_guest_catalog_access(self):
        # Guest can browse products
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Industrial Steel Bolts')

    def test_signup_constraints(self):
        # Signup as buyer
        response = self.client.post(reverse('signup'), {
            'username': 'newbuyer',
            'email': 'newbuyer@test.com',
            'role': 'buyer',
            'profile_picture': self.get_dummy_image(),
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        })
        self.assertEqual(response.status_code, 302) # Redirect to dashboard
        user = UserProfile.objects.get(username='newbuyer')
        self.assertEqual(user.role, 'buyer')
        self.assertEqual(user.raw_password_view, 'newpassword')

    def test_vendor_employee_management(self):
        self.client.login(username='vendor1', password=self.vendor_pwd)
        # Create shipper employee
        response = self.client.post(reverse('vendor_create_employee'), {
            'username': 'logistics_shipper',
            'email': 'shipagent@scm.com',
            'role': 'shipper',
            'profile_picture': self.get_dummy_image(),
            'password': 'emppassword123'
        })
        self.assertEqual(response.status_code, 302)
        emp = UserProfile.objects.get(username='logistics_shipper')
        self.assertEqual(emp.role, 'shipper')
        self.assertEqual(emp.raw_password_view, 'emppassword123')

    def test_order_placement_and_supply_chain_lifecycle(self):
        # 1. Login as Buyer & Place Order
        self.client.login(username='buyer1', password=self.buyer_pwd)
        
        # Test checkout page load
        response = self.client.get(reverse('checkout', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)

        # Place order
        response = self.client.post(reverse('checkout', args=[self.product.id]), {
            'quantity': 2,
            'payment_method': 'cod'
        })
        self.assertEqual(response.status_code, 302) # Redirect to orders dashboard

        # Verify Order is Confirmed and OTP is generated
        order = Order.objects.latest('id')
        self.assertEqual(order.status, 'confirmed')
        self.assertEqual(order.quantity, 2)
        self.assertEqual(order.total_price, 270.00) # 135.00 * 2
        self.assertTrue(len(order.otp) == 6)
        self.assertIsNotNone(order.order_confirmed_at)
        
        # Verify inventory stock decrement
        self.product.refresh_from_db()
        self.assertEqual(self.product.available_quantity, 98)

        # 2. Login as Shipper -> Transition to Shipped
        self.client.login(username='shipper1', password='shipperpassword')
        response = self.client.post(reverse('update_status_shipper', args=[order.id]))
        self.assertEqual(response.status_code, 302)
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'shipped')
        self.assertIsNotNone(order.shipped_at)

        # 3. Login as Out for Delivery -> Transition to Out for Delivery
        self.client.login(username='ofd1', password='ofdpassword')
        response = self.client.post(reverse('update_status_out_for_delivery', args=[order.id]))
        self.assertEqual(response.status_code, 302)

        order.refresh_from_db()
        self.assertEqual(order.status, 'out_for_delivery')
        self.assertIsNotNone(order.out_for_delivery_at)

        # 4. Login as Delivered agent -> Complete delivery with OTP
        self.client.login(username='delivered1', password='deliveredpassword')
        
        # Try invalid OTP first
        response = self.client.post(reverse('verify_otp_and_deliver', args=[order.id]), {
            'otp': '000000'
        })
        order.refresh_from_db()
        self.assertNotEqual(order.status, 'delivered')

        # Provide correct OTP
        response = self.client.post(reverse('verify_otp_and_deliver', args=[order.id]), {
            'otp': order.otp
        })
        self.assertEqual(response.status_code, 302)
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'delivered')
        self.assertIsNotNone(order.delivered_at)

    def test_pdf_receipt_download(self):
        # Buyer places order
        self.client.login(username='buyer1', password=self.buyer_pwd)
        self.client.post(reverse('checkout', args=[self.product.id]), {
            'quantity': 1,
            'payment_method': 'cod'
        })
        order = Order.objects.latest('id')

        # Download receipt
        response = self.client.get(reverse('generate_receipt_pdf', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_vendor_approval_workflow(self):
        # 1. Register a new vendor and verify they are not approved by default
        response = self.client.post(reverse('signup'), {
            'username': 'newvendor',
            'email': 'newvendor@test.com',
            'role': 'vendor',
            'profile_picture': self.get_dummy_image(),
            'password': 'vendorpwd123',
            'confirm_password': 'vendorpwd123'
        })
        self.assertEqual(response.status_code, 302)
        
        vendor_user = UserProfile.objects.get(username='newvendor')
        self.assertFalse(vendor_user.is_approved)

        # 2. Login as the unapproved vendor and verify dashboard states
        self.client.login(username='newvendor', password='vendorpwd123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Waiting for approval')

        # 3. Verify unapproved vendor is blocked from creating products/employees
        response = self.client.post(reverse('vendor_add_product'), {
            'name': 'Restricted Block',
            'price': 100,
            'available_quantity': 5,
            'image1': self.get_dummy_image()
        })
        self.assertEqual(response.status_code, 302) # Redirect due to validation/block
        self.assertFalse(Product.objects.filter(name='Restricted Block').exists())

        # 4. Create an employee and check linkage, then verify employee is suspended if vendor not approved
        # In setup, let's link self.shipper to this new vendor
        self.shipper.created_by = vendor_user
        self.shipper.save()

        # Login as employee
        self.client.login(username=self.shipper.username, password='shipperpassword')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Waiting for approval')

        # Create admin user
        admin_user = UserProfile.objects.create_superuser(
            username='system_admin',
            email='admin@scm.com',
            password='adminpassword',
            role='admin'
        )

        # 5. Log in as Admin and Approve the Vendor
        self.client.login(username='system_admin', password='adminpassword')
        response = self.client.post(reverse('admin_approve_vendor', args=[vendor_user.id]))
        self.assertEqual(response.status_code, 302)
        
        vendor_user.refresh_from_db()
        self.assertTrue(vendor_user.is_approved)

        # 6. Verify employee is no longer suspended
        self.client.login(username=self.shipper.username, password='shipperpassword')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Waiting for approval')

    def test_admin_creation_by_another_admin(self):
        admin_user = UserProfile.objects.create_superuser(
            username='system_admin',
            email='admin@scm.com',
            password='adminpassword',
            role='admin'
        )
        self.client.login(username='system_admin', password='adminpassword')
        
        response = self.client.post(reverse('admin_create_admin'), {
            'username': 'sub_admin',
            'email': 'subadmin@scm.com',
            'profile_picture': self.get_dummy_image(),
            'password': 'subadminpassword'
        })
        self.assertEqual(response.status_code, 302)
        
        sub_admin = UserProfile.objects.get(username='sub_admin')
        self.assertEqual(sub_admin.role, 'admin')
        self.assertTrue(sub_admin.is_superuser)
        self.assertTrue(sub_admin.is_staff)

    def test_admin_approval_restrictions(self):
        admin_user = UserProfile.objects.create_superuser(
            username='system_admin',
            email='admin@scm.com',
            password='adminpassword',
            role='admin'
        )
        sub_admin = UserProfile.objects.create_superuser(
            username='sub_admin',
            email='subadmin@scm.com',
            password='subadminpassword',
            role='admin'
        )
        self.client.login(username='system_admin', password='adminpassword')
        
        # Admin trying to disapprove themselves
        response = self.client.post(reverse('admin_disapprove_vendor', args=[admin_user.id]))
        self.assertEqual(response.status_code, 302)
        admin_user.refresh_from_db()
        self.assertTrue(admin_user.is_approved)
        
        # Admin trying to disapprove another admin
        response = self.client.post(reverse('admin_disapprove_vendor', args=[sub_admin.id]))
        self.assertEqual(response.status_code, 302)
        sub_admin.refresh_from_db()
        self.assertTrue(sub_admin.is_approved)

    def test_vendor_disapproval_propagation(self):
        admin_user = UserProfile.objects.create_superuser(
            username='system_admin',
            email='admin@scm.com',
            password='adminpassword',
            role='admin'
        )
        
        # Associate shipper with vendor
        self.shipper.created_by = self.vendor
        self.shipper.save()
        
        self.client.login(username='system_admin', password='adminpassword')
        
        # Disapprove vendor
        response = self.client.post(reverse('admin_disapprove_vendor', args=[self.vendor.id]))
        self.assertEqual(response.status_code, 302)
        
        self.vendor.refresh_from_db()
        self.shipper.refresh_from_db()
        self.assertFalse(self.vendor.is_approved)
        self.assertFalse(self.shipper.is_approved)

    def test_search_functions(self):
        # 1. Product search in Catalog
        response = self.client.get(reverse('home'), {'search_products': 'Bolts'})
        self.assertContains(response, 'Industrial Steel Bolts')
        
        # 2. Buyer dashboard searches
        self.client.login(username='buyer1', password=self.buyer_pwd)
        response = self.client.get(reverse('dashboard'), {'search_products': 'Steel'})
        self.assertContains(response, 'Industrial Steel Bolts')
        
        # Create an order for buyer
        order = Order.objects.create(
            product=self.product,
            buyer=self.buyer,
            quantity=1,
            total_price=135.00,
            status='confirmed'
        )
        response = self.client.get(reverse('dashboard'), {'tab': 'orders', 'search_orders': 'Bolts'})
        self.assertContains(response, 'Industrial Steel Bolts')

        # 3. Vendor dashboard searches
        self.client.login(username='vendor1', password=self.vendor_pwd)
        
        # Search employee in vendor list
        self.shipper.created_by = self.vendor
        self.shipper.save()
        response = self.client.get(reverse('dashboard'), {'tab': 'employees', 'search_employees': 'shipper'})
        self.assertContains(response, 'shipper1')

    def test_excel_audit_report_generation(self):
        admin_user = UserProfile.objects.create_superuser(
            username='system_admin',
            email='admin@scm.com',
            password='adminpassword',
            role='admin'
        )
        self.shipper.created_by = self.vendor
        self.shipper.save()
        
        self.client.login(username='system_admin', password='adminpassword')
        response = self.client.get(reverse('export_audit_report_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertTrue(len(response.content) > 0)


