# Implementation Plan - Vendor Approval and Admin Dashboard Controls

We will add a Vendor approval workflow. When a vendor signs up, their account remains inactive (disabled capabilities) until approved by the administrator. Disapproving a vendor also suspends the logistics employees they created.

## User Review Required

> [!IMPORTANT]
> - **Database Schema Migration**: We will add `is_approved` (Boolean) and `created_by` (ForeignKey to self) to `UserProfile`. Default migrations will be run.
> - **Admin Dashboard**: We will update the `/dashboard/` view to render a specialized Admin control panel for superusers. This panel includes tabs for "Logistic Accounts" and "Vendor ID", allowing the admin to approve/disapprove vendors.

## Open Questions

None at this time.

## Proposed Changes

### Component: Core App

#### [MODIFY] [models.py](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/models.py)
- Add `is_approved = models.BooleanField(default=True)` to `UserProfile`. During signup, if role is `vendor`, set `is_approved = False`.
- Add `created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='employees_created')` to `UserProfile` to track creator relationship for logistics agents.

#### [MODIFY] [views.py](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/views.py)
- In `signup_view`: If registered user is a `vendor`, save with `is_approved = False`. Otherwise, default is `True`.
- In `vendor_create_employee`: Set `employee.created_by = request.user`.
- In `dashboard_view`:
  - If `request.user.is_superuser`: Render a new template `core/admin_dashboard.html`.
  - For vendors, check if `user.is_approved == False`. If so, set context flag `waiting_approval = True`.
  - For logistics employees (shipper, out_for_delivery, delivered), check if `user.created_by` exists and is NOT approved. If so, set context flag `waiting_approval = True`.
- Add new views:
  - `admin_approve_vendor(request, vendor_id)`: Marks vendor `is_approved = True`.
  - `admin_disapprove_vendor(request, vendor_id)`: Marks vendor `is_approved = False`.

#### [NEW] [admin_dashboard.html](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/templates/core/admin_dashboard.html)
- Dashboard layout for superusers containing:
  - Tab 1: **Logistic Accounts** (lists all logistics employee accounts in SCM database).
  - Tab 2: **Vendor ID** (lists all vendors with "Approve" and "Disapprove" buttons).

#### [MODIFY] templates
- [vendor_dashboard.html](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/templates/core/vendor_dashboard.html): If `waiting_approval` is active, hide/disable all form fields, product additions, and SCM capabilities. Display a prominent "Waiting for approval" message.
- [shipper_dashboard.html](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/templates/core/shipper_dashboard.html), [out_for_delivery_dashboard.html](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/templates/core/out_for_delivery_dashboard.html), [delivered_dashboard.html](file:///Users/abhisheksharma/Documents/05 VS Code/16_B2B_Full_Stack/core/templates/core/delivered_dashboard.html): If `waiting_approval` is active, display "Waiting for approval" status alert and disable transit dispatch forms.

---

## Verification Plan

### Automated Tests
- Update `core/tests.py` to check:
  - A registered vendor is NOT approved by default and sees "Waiting for approval".
  - Admin approves vendor, and the vendor gets active capabilities.
  - Disapproving a vendor also blocks SCM capabilities for the associated logistics employee.
- Run tests: `python manage.py test`.

### Manual Verification
- Register a vendor account, log in, verify "Waiting for approval" banner and disabled controls.
- Log in as `admin`, approve the vendor, verify vendor capabilities unlock.
- Disapprove vendor, check that vendor's shipper agent sees the block alert.
