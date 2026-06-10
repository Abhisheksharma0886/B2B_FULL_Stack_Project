# Implementation Plan - Admin Upgrades, SCM Search, and Excel Audit Reports

This plan outlines changes to design admin creation workflows, separate admin/superuser roles, introduce search capabilities across SCM modules, filter logistics employees, and export formatted Excel audit reports.

## User Review Required

> [!IMPORTANT]
> - **Excel Library Dependency**: We will use `openpyxl` to write native Excel spreadsheets (.xlsx) for SCM logistics audit reports. This library has been installed successfully.
> - **Role Separation**: Admin superusers will be designated as the `'admin'` role and filtered out from Vendor ID tables to prevent self-approvals/disapprovals.

## Open Questions

None. All requirements are clear.

## Proposed Changes

### Component: Database Models & Forms

#### [MODIFY] [models.py](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/models.py)
- Add `'admin'` to `ROLE_CHOICES` in `UserProfile`.
- Ensure default superuser setup writes `role='admin'`.

#### [MODIFY] [forms.py](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/forms.py)
- Create `AdminCreationForm`: Form for superusers to create other admin accounts. When saved, sets `is_superuser=True`, `is_staff=True`, `is_approved=True`, and `role='admin'`.

---

### Component: SCM Views & Controller Logic

#### [MODIFY] [views.py](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/views.py)
1. **Search Integration**:
   - In `home_view`, filter product query (`search_products`).
   - In `dashboard_view`:
     - For Buyer: Filter products (`search_products`) and orders (`search_orders`).
     - For Vendor: Filter products (`search_products`), orders (`search_orders`), and employees (`search_employees`).
     - For Shippers/OFD/Delivered: Filter pending orders.
     - For Admin: Filter employees (`search_employees` by username, email, or role), vendors (`search_vendors`).
2. **Admin Creation & Role Controls**:
   - Create `admin_create_admin` view: Processes superuser submissions of `AdminCreationForm`.
   - Update `admin_approve_vendor` and `admin_disapprove_vendor` views:
     - Check and reject if an admin attempts to approve/disapprove themselves or another admin.
     - Disapproving a vendor sets `is_approved = False` for all employee accounts where `created_by = vendor`.
3. **Logistics Filtering & Excel Export**:
   - In `dashboard_view`, support vendor filter for logistics employees (`filter_vendor` dropdown).
   - Create view `export_audit_report_excel(request)`:
     - Fetches logistics employees matching the current `filter_vendor` and `search_employees` query.
     - Generates a styled Excel workbook with openpyxl and returns it as a download file.

---

### Component: Templates & UI Upgrades

#### [MODIFY] [admin_dashboard.html](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/templates/core/admin_dashboard.html)
- Add a new tab: **Create Admin ID** displaying the `AdminCreationForm`.
- In the **Logistic Accounts** tab:
  - Add search bar and Vendor filter dropdown.
  - Add a button "Export Audit Report (Excel)" which queries the Excel download URL with the active search/filter parameters.
  - Ensure the "Creator Vendor" column displays the creator's username prominently.
- In the **Vendor ID** tab:
  - Add search bar for vendors.
  - Ensure superuser accounts are not listed.

#### [MODIFY] [vendor_dashboard.html](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/templates/core/vendor_dashboard.html)
- Add search bars to Products, Orders, and Employees lists.

#### [MODIFY] [buyer_dashboard.html](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/templates/core/buyer_dashboard.html)
- Add search bars to Products and Orders lists.

#### [MODIFY] [home.html](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/templates/core/home.html)
- Add search bar to catalog.

---

## Verification Plan

### Automated Tests
- Update `core/tests.py`:
  - Test admin creation.
  - Test search functionalities across product, order, and employee views.
  - Test that disapprove propagation sets `is_approved = False` on employee accounts.
  - Test Excel audit report downloading.
- Run tests: `python manage.py test`.

### Manual Verification
- Log in as admin, verify "Create Admin ID" tab, and add another admin account.
- Try to approve/disapprove self or other admin accounts (verify rejection).
- Filter logistics staff by Vendor and download Excel audit report. Verify formatting.
- Search for a specific product, order, and logistics employee.
