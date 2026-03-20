from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import F
from django.db import transaction
import json, uuid

from .models import FoodCart, MenuItem, CartSchedule, OrderLobby, LobbyItem
from .forms import VendorRegistrationForm, MenuItemForm, CartSettingsForm, ScheduleForm

# --- PUBLIC VIEWS ---

def map_view(request):
    """Renders the HTML page with the map"""
    # Just render the template; the JS handles the data fetching
    return render(request, 'vendor/live_map.html')

def vendor_list(request):
    """Shows all carts with calculated Open/Closed status"""
    carts = FoodCart.objects.all()
    now = timezone.localtime().time()
    
    for cart in carts:
        # Check 1: Is the manual "Open for Business" switch ON?
        if not cart.is_open:
            cart.is_open_now = False
            continue

        # Check 2: Time Logic (Handles Midnight Carts too)
        # If closing time is smaller than opening time (e.g. 6PM to 2AM), use special logic
        if cart.closing_time < cart.opening_time:
             # Open if it's after start OR before end (e.g. it's 1 AM)
             is_time_ok = now >= cart.opening_time or now <= cart.closing_time
        else:
             # Standard day (e.g. 10AM to 10PM)
             is_time_ok = cart.opening_time <= now <= cart.closing_time
        
        cart.is_open_now = is_time_ok
            
    return render(request, 'vendor/list.html', {'carts': carts})

def menu_view(request, cart_id):
    cart = get_object_or_404(FoodCart, id=cart_id)
    items = cart.items.filter(is_available=True)
    
    # --- NEW LOGIC: Get Current Bill ---
    session_key = f'cart_{cart.id}_total'
    my_total = request.session.get(session_key, 0)
    # -----------------------------------

    return render(request, 'vendor/menu.html', {
        'cart': cart, 
        'items': items,
        'my_total': my_total  # Pass it to template
    })


# --- API ENDPOINTS ---

def get_cart_location(request):
    """API that returns a list of ALL carts for the Map"""
    # We return ALL carts so the map can show closed ones too (optional)
    # or you can filter by is_open=True if you prefer
    carts = FoodCart.objects.all()
    
    cart_list = []
    for cart in carts:
        cart_list.append({
            'id': cart.id,
            'name': cart.name,
            'lat': cart.current_lat,
            'long': cart.current_long,
            'url': f"/vendor/menu/{cart.id}/",
            'image_url': cart.image.url if cart.image else "",
        })
    
    return JsonResponse({'carts': cart_list})

@login_required
def update_location_api(request):
    """API to receive GPS data from the Vendor Dashboard"""
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            cart = request.user.foodcart
            cart.current_lat = data.get('lat')
            cart.current_long = data.get('long')
            cart.save()
            return JsonResponse({'status': 'success', 'message': 'Location Updated!'})
        except FoodCart.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'No cart found'}, status=403)
    
    return JsonResponse({'status': 'fail'}, status=400)


# --- VENDOR DASHBOARD & MANAGEMENT ---

@login_required
def vendor_dashboard(request):
    try:
        cart = request.user.foodcart
    except FoodCart.DoesNotExist:
        return render(request, 'vendor/no_cart_error.html')
    return render(request, 'vendor/dashboard.html', {'cart': cart})

def vendor_register(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            FoodCart.objects.create(
                owner=user,
                name=form.cleaned_data['cart_name'],
                current_lat=12.9716, 
                current_long=77.5946
            )
            login(request, user)
            return redirect('vendor_dashboard')
    else:
        form = VendorRegistrationForm()
    return render(request, 'vendor/register.html', {'form': form})

@login_required
def delete_cart(request):
    """Permanently deletes the vendor's cart and logs them out"""
    try:
        cart = request.user.foodcart
        
        if request.method == 'POST':
            # 1. Delete the Cart (and all menus, schedules, etc. cascade delete)
            cart.delete()
            
            # 2. Log them out
            logout(request)
            
            # 3. Message and Redirect
            messages.success(request, "Your cart has been deleted. We are sorry to see you go!")
            return redirect('home')
            
    except FoodCart.DoesNotExist:
        messages.error(request, "No cart found to delete.")
        return redirect('vendor_dashboard')

    # If they tried to access via GET, just send them back
    return redirect('cart_settings')

@login_required
def manage_menu(request):
    cart = request.user.foodcart
    items = cart.items.all()
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.cart = cart
            item.save()
            return redirect('manage_menu')
    else:
        form = MenuItemForm()
    return render(request, 'vendor/manage_menu.html', {'items': items, 'form': form, 'cart': cart})

@login_required
def cart_settings(request):
    cart = request.user.foodcart
    if request.method == 'POST':
        form = CartSettingsForm(request.POST, request.FILES, instance=cart)
        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')
    else:
        form = CartSettingsForm(instance=cart)
    return render(request, 'vendor/cart_settings.html', {'form': form})

@login_required
def manage_schedule(request):
    cart = request.user.foodcart
    schedules = cart.schedule.all()
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.cart = cart
            schedule.save()
            return redirect('manage_schedule')
    else:
        form = ScheduleForm()
    return render(request, 'vendor/manage_schedule.html', {'form': form, 'schedules': schedules})

@login_required
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(CartSchedule, id=schedule_id, cart=request.user.foodcart)
    schedule.delete()
    return redirect('manage_schedule')


# --- ORDERING & PARTY MODE ---

# vendor/views.py

def order_item(request, item_id):
    if request.method == "POST":
        with transaction.atomic():
            item = MenuItem.objects.select_for_update().get(id=item_id)
            if item.stock_qty > 0:
                item.stock_qty = F('stock_qty') - 1
                item.save()
                
                # --- FIX: Convert Decimal to Float ---
                session_key = f'cart_{item.cart.id}_total'
                current_total = request.session.get(session_key, 0)
                
                # We wrap item.price in float() to make it JSON serializable
                new_total = float(current_total) + float(item.price)
                request.session[session_key] = new_total
                # -------------------------------------
                
                messages.success(request, f"Ordered {item.name}!")
            else:
                messages.error(request, f"Sorry! {item.name} is sold out.")
                
    # Redirect back to the menu
    return redirect('menu_view', cart_id=item.cart.id)

def start_party(request, cart_id):
    """Creates a new lobby LINKED to a specific cart"""
    cart = get_object_or_404(FoodCart, id=cart_id) # Get the specific cart
    
    lobby = OrderLobby.objects.create(cart=cart) # Save it to the lobby
    
    request.session['lobby_id'] = str(lobby.code)
    request.session['user_name'] = request.user.username if request.user.is_authenticated else "Host"
    
    return redirect('party_menu', lobby_code=lobby.code)

def join_party(request, lobby_code):
    lobby = get_object_or_404(OrderLobby, code=lobby_code)
    request.session['lobby_id'] = str(lobby.code)
    if 'user_name' not in request.session:
        request.session['user_name'] = f"Guest-{uuid.uuid4().hex[:4]}"
    return redirect('party_menu', lobby_code=lobby.code)

def party_menu(request, lobby_code):
    lobby = get_object_or_404(OrderLobby, code=lobby_code)
    
    # --- THE FIX ---
    # Instead of FoodCart.objects.first(), we use the saved cart
    cart = lobby.cart 
    # ---------------
    
    items = cart.items.filter(is_available=True)
    shared_items = lobby.items.all()
    total_price = sum(item.price for item in shared_items)

    # (Keep your split bill logic here from the previous step)
    contributors = set(item.added_by for item in shared_items)
    user_count = len(contributors)
    split_amount = round(total_price / user_count, 2) if user_count > 0 else 0

    return render(request, 'vendor/party_menu.html', {
        'cart': cart, 
        'items': items, 
        'lobby': lobby,
        'shared_items': shared_items,
        'total_price': total_price,
        'user_count': user_count,       # For the bill split
        'split_amount': split_amount,   # For the bill split
        'my_name': request.session.get('user_name')
    })

def add_to_party(request, lobby_code, item_id):
    lobby = get_object_or_404(OrderLobby, code=lobby_code)
    item = get_object_or_404(MenuItem, id=item_id)
    LobbyItem.objects.create(
        lobby=lobby,
        item_name=item.name,
        price=item.price,
        added_by=request.session.get('user_name', 'Anonymous')
    )
    return redirect('party_menu', lobby_code=lobby_code)

def remove_from_party(request, lobby_code, item_id):
    lobby_item = get_object_or_404(LobbyItem, id=item_id, lobby__code=lobby_code)
    lobby_item.delete()
    return redirect('party_menu', lobby_code=lobby_code)

def pay_bill(request, lobby_code):
    """Simulates payment and clears the lobby"""
    lobby = get_object_or_404(OrderLobby, code=lobby_code)
    
    # 1. Delete all items (Clear the table)
    lobby.items.all().delete()
    
    # 2. Show Success Message
    messages.success(request, "Bill paid successfully! The lobby is now open for new orders.")
    
    return redirect('party_menu', lobby_code=lobby.code)

@login_required
def delete_menu_item(request, item_id):
    """Deletes a specific menu item"""
    # We ensure the item belongs to the logged-in user's cart for security
    item = get_object_or_404(MenuItem, id=item_id, cart=request.user.foodcart)
    
    item.delete()
    messages.success(request, "Item removed from menu.")
    return redirect('manage_menu')

# --- EDIT ITEM VIEW ---
@login_required
def edit_menu_item(request, item_id):
    """Updates an existing menu item"""
    item = get_object_or_404(MenuItem, id=item_id, cart=request.user.foodcart)
    
    if request.method == 'POST':
        # We pass 'instance=item' so Django knows we are UPDATING, not creating
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated successfully!")
            return redirect('manage_menu')
    else:
        # Pre-fill the form with existing data
        form = MenuItemForm(instance=item)
        
    return render(request, 'vendor/edit_menu_item.html', {'form': form, 'item': item})

def pay_individual_bill(request, cart_id):
    """Clears the session total for this cart"""
    session_key = f'cart_{cart_id}_total'
    if session_key in request.session:
        del request.session[session_key]
        
    messages.success(request, "Payment recorded! Your bill is cleared.")
    return redirect('menu_view', cart_id=cart_id)