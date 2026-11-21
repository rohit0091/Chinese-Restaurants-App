from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomerProfile, Address
from orders.models import Order

def login_view(request):
    """
    Renders login view and processes credential authentication.
    """
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # Support email or username login
        user = None
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            user = authenticate(username=username_or_email, password=password)
            
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username/email or password.")
            
    return render(request, 'accounts/login.html')

def signup_view(request):
    """
    Handles new user creation, password verification, and profile instantiation.
    """
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        phone = request.POST.get('phone', '').strip()
        
        if not username or not email or not password:
            messages.error(request, "Please fill in all mandatory fields.")
        elif password != password_confirm:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        else:
            # Create user
            user = User.objects.create_user(username=username, email=email, password=password)
            # Create associated profile
            CustomerProfile.objects.create(user=user, phone=phone)
            
            # Log user in
            login(request, user)
            messages.success(request, "Registration successful! Welcome to Mahato Chinese Center.")
            return redirect('home')
            
    return render(request, 'accounts/signup.html')

def logout_view(request):
    """
    Standard logout handler.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

@login_required
def profile_view(request):
    """
    Customer profile dashboard displaying orders, addresses, and profiles.
    """
    profile, created = CustomerProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:10]
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        profile.phone = phone
        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')
        
    context = {
        'profile': profile,
        'orders': orders,
        'addresses': addresses,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def add_address(request):
    """
    Adds a shipping address to the user's address book.
    """
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address_line_1 = request.POST.get('address_line_1', '').strip()
        address_line_2 = request.POST.get('address_line_2', '').strip()
        landmark = request.POST.get('landmark', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        address_type = request.POST.get('address_type', 'HOME').strip()
        is_default = request.POST.get('is_default') == 'on'
        
        if not full_name or not phone or not address_line_1 or not city or not state or not pincode:
            messages.error(request, "Please fill in all required fields.")
        else:
            if is_default:
                # Set others to False
                Address.objects.filter(user=request.user).update(is_default=False)
                
            Address.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                landmark=landmark,
                city=city,
                state=state,
                pincode=pincode,
                address_type=address_type,
                is_default=is_default
            )
            messages.success(request, "Address added successfully.")
            return redirect('profile')
            
    return render(request, 'accounts/address_form.html')

@login_required
def delete_address(request, address_id):
    """
    Deletes an address from the address book.
    """
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully.")
    return redirect('profile')

@login_required
def set_default_address(request, address_id):
    """
    Marks an address as default for shipping.
    """
    Address.objects.filter(user=request.user).update(is_default=False)
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, f"Set {address.get_address_type_display()} address as default.")
    return redirect('profile')
