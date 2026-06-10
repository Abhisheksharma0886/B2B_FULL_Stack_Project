# Implementation Plan - B2P E-Commerce and Supply Chain Management App

This plan details the implementation of a full-featured B2P E-commerce and Supply Chain Management web application using Django, SQLite, and ReportLab. It implements a role-based workflow with five user roles (Buyer, Vendor, Shipper, Out for Delivery, Delivered), order tracking with OTP verification, PDF invoice receipt generation, and a customized Django Admin interface.

## User Review Required

> [!IMPORTANT]
> - **Superuser Creation**: The Django admin superuser will be pre-configured with the credentials `admin` / `admin123` via a Django command/script.
> - **Plain-text Password Debugging**: Per the user request, we will store a plain text password copy in the custom User Profile model under the field `raw_password_view` so the Admin can inspect user credentials directly in the admin panel for debugging.
> - **Payment Option UI**: Online payment options will be visible in the checkout layout but marked as "Currently Not Available" and disabled, defaulting to "Cash on Delivery".

## Open Questions

None at this time. All requirements are clear and specified.

## Proposed Changes

### Component: Django Project and App Layout

We will initialize a new Django project named `b2p_management` and a Django app named `core`.

#### [NEW] [settings.py](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/b2p_management/settings.py)
- Configure SQLite3 database.
- Configure `AUTH_USER_MODEL` to `core.UserProfile`.
- Configure Static and Media settings (`STATIC_URL`, `MEDIA_URL`, `MEDIA_ROOT`, `STATICFILES_DIRS`).
- Add standard Django configurations and app lists.

#### [NEW] [models.py](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/models.py)
Define three core database models:
1. `UserProfile(AbstractUser)`:
   - `role`: Choices: `buyer`, `vendor`, `shipper`, `out_for_delivery`, `delivered`.
   - `profile_picture`: compulsory ImageField.
   - `raw_password_view`: CharField to store plain-text password for admin debugging.
2. `Product`:
   - `vendor`: ForeignKey to UserProfile.
   - `name`: CharField.
   - `description`: TextField.
   - `price`: DecimalField.
   - `available_quantity`: IntegerField.
   - `offer_percentage`: DecimalField.
   - `image1` to `image5`: ImageFields (compulsory or fallback placeholder).
3. `Order`:
   - `product`: ForeignKey to Product.
   - `buyer`: ForeignKey to UserProfile.
   - `quantity`: IntegerField.
   - `total_price`: DecimalField.
   - `payment_method`: CharField.
   - `status`: ChoiceField: `Order Confirmed`, `Shipped`, `Out for Delivery`, `Delivered`.
   - `otp`: 6-digit Auto-Generated OTP string.
   - `order_confirmed_at`, `shipped_at`, `out_for_delivery_at`, `delivered_at`: DateTimeFields.

#### [NEW] [forms.py](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/forms.py)
- Custom public SignupForm (Buyer and Vendor only).
- Employee creation Form (Shipper, Out for Delivery, Delivered) used in the Vendor Dashboard.
- Product creation/editing Form.
- Checkout/Order creation Form.

#### [NEW] [admin.py](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/admin.py)
- Register Custom UserProfile, Product, and Order tables.
- Display `Username`, `Email`, `Role`, `raw_password_view`, and a clickable `Profile Image preview`.

#### [NEW] [views.py](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/views.py)
Implement views:
- `home_view`: Listing all products. Unauthenticated users see products. Clicking triggers a login modal.
- `signup_view` and `login_view`: Login/signup forms. Redirects to appropriate dashboards based on role.
- `dashboard_view`: Main portal routing the logged-in user to their respective dashboard:
  - Buyer Dashboard: Product browsing, order placing, active order tracking with stepper & OTP view, receipt downloading.
  - Vendor Dashboard: Create Employee, add product, list their products, list orders.
  - Shipper Dashboard: List "Order Confirmed" orders, update to "Shipped".
  - Out for Delivery Dashboard: List "Shipped" orders, update to "Out for Delivery".
  - Delivered Dashboard: List "Out for Delivery" orders, input OTP verification to mark as "Delivered".
- `generate_receipt_pdf`: ReportLab PDF view to generate receipt documents.

#### [NEW] [urls.py](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/urls.py) and [b2p_management/urls.py](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/b2p_management/urls.py)
Define URL routing for dashboards, authentication, orders, employee creation, and receipt PDF downloads.

#### Templates Layout
- `base.html`: Common layout with modern styling (sleek dark navigation, Bootstrap for responsive components, custom CSS animations/glassmorphism).
- `home.html`: Product list grid. Product card links trigger a login popup modal for guest users.
- `login.html`, `signup.html`: Beautiful styling.
- `buyer_dashboard.html`, `vendor_dashboard.html`: Beautiful multi-panel user dashboards.
- `shipper_dashboard.html`, `out_for_delivery_dashboard.html`, `delivered_dashboard.html`: Status update dashboards.

---

## Verification Plan

### Automated Tests
- Create standard Django test cases verifying role-based logins, order flow transitions (Confirmed -> Shipped -> Out for Delivery -> Delivered via OTP), and access restrictions.
- Run tests via `python manage.py test`.

### Manual Verification
- Run local development server: `python manage.py runserver`.
- Test unauthenticated behavior (modal popup).
- Create a superuser, log into admin panel, check details.
- Register Buyer and Vendor accounts.
- In Vendor dashboard, add a product with 5 images and create three logistics employees.
- Purchase a product from Buyer dashboard using Cash.
- Follow order updates sequentially using logistics agent credentials.
- Generate and download order receipt PDFs.
