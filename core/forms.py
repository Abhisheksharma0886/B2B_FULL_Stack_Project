from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile, Product, Order

User = get_user_model()

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password', 'class': 'form-control'}), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}), required=True)
    role = forms.ChoiceField(
        choices=[('buyer', 'Buyer'), ('vendor', 'Vendor')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    profile_picture = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=True, # Compulsory profile picture upload for account creation
        help_text="Upload your profile picture (Compulsory)"
    )

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter Username', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Email Address', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        user.set_password(self.cleaned_data['password'])
        # Save raw password for admin debugging as requested
        user.raw_password_view = self.cleaned_data['password']
        if user.role == 'vendor':
            user.is_approved = False
        if commit:
            user.save()
        return user

class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Employee Password', 'class': 'form-control'}), required=True)
    role = forms.ChoiceField(
        choices=[
            ('shipper', 'Shipper ID (Logistics Employee)'),
            ('out_for_delivery', 'Out for Delivery ID (Logistics Employee)'),
            ('delivered', 'Delivered ID (Delivery Agent)')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    profile_picture = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=True, # Compulsory profile picture upload for employee creation
        help_text="Upload employee profile picture (Compulsory)"
    )

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter Employee Username', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Employee Email', 'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is already taken.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        user.set_password(self.cleaned_data['password'])
        # Save raw password for admin debugging
        user.raw_password_view = self.cleaned_data['password']
        if commit:
            user.save()
        return user

class ProductForm(forms.ModelForm):
    image1 = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}), required=True, help_text="Primary Image (Compulsory)")
    image2 = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}), required=False)
    image3 = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}), required=False)
    image4 = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}), required=False)
    image5 = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'available_quantity', 'offer_percentage', 'image1', 'image2', 'image3', 'image4', 'image5']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Product Name', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Product Description', 'rows': 3, 'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Price (INR)', 'min': '0', 'step': '0.01', 'class': 'form-control'}),
            'available_quantity': forms.NumberInput(attrs={'placeholder': 'Available Quantity', 'min': '0', 'class': 'form-control'}),
            'offer_percentage': forms.NumberInput(attrs={'placeholder': 'Offer/Discount Percentage', 'min': '0', 'max': '100', 'step': '0.01', 'class': 'form-control'}),
        }

class OrderForm(forms.ModelForm):
    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        initial=1,
        min_value=1,
        required=True
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('cod', 'Cash on Delivery (COD)'),
            ('card', 'Credit/Debit Card (Currently Not Available)'),
            ('upi', 'UPI (Currently Not Available)'),
            ('netbanking', 'Net Banking (Currently Not Available)')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='cod',
        required=True
    )

    class Meta:
        model = Order
        fields = ['quantity', 'payment_method']

class AdminCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Admin Password', 'class': 'form-control'}), required=True)
    profile_picture = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=True, # Compulsory profile picture upload for admin creation
        help_text="Upload admin profile picture (Compulsory)"
    )

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter Admin Username', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter Admin Email', 'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username is already taken.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'admin'
        user.is_superuser = True
        user.is_staff = True
        user.is_approved = True
        user.set_password(self.cleaned_data['password'])
        # Save raw password for admin debugging
        user.raw_password_view = self.cleaned_data['password']
        if commit:
            user.save()
        return user

