from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model # Added to fetch User model
from bookings.models import Booking
from contributions.models import Contribution
from safety.models import SOSAlert
from django.db.models import Sum
from temples.models import Temple
from bookings.models import DarshanSlot
from django.http import JsonResponse
from django.utils import timezone
from django.utils import timezone


User = get_user_model()

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('user_dashboard')
        
    context = {
        # Total pilgrims = total tickets booked across all temples
        'total_users': Booking.objects.aggregate(total=Sum('ticket_count'))['total'] or 0,
        
        # Passes already scanned at the gate (Requirement E.6)
        'used_bookings': Booking.objects.filter(status='USED').count(),
        
        # Valid bookings currently in the system
        'total_bookings': Booking.objects.filter(status='VALID').count(),
        
        # Financial sum (Requirement J.9)
        'total_dakshan': Contribution.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
        
        # Emergency metrics (Requirement J.7)
        'active_sos': SOSAlert.objects.filter(status='PENDING').count(),
        'recent_sos': SOSAlert.objects.filter(status='PENDING').order_by('-created_at')[:5],
    }
    return render(request, 'management/admin_dashboard.html', context)

@login_required
def qr_scanner_page(request):
    # This renders the camera interface
    return render(request, 'management/qr_scanner.html')

@login_required
def validate_booking(request, booking_uuid):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request
        if request.user.role != 'admin':
            return JsonResponse({'success': False, 'message': 'Access denied'})

        try:
            booking = Booking.objects.get(booking_id=booking_uuid)
        except Booking.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid booking'})

        if booking.slot.date != timezone.localdate():
            return JsonResponse({'success': False, 'message': 'Ticket is not for today'})

        if booking.status == 'VALID':
            booking.status = 'USED'
            booking.save()
            return JsonResponse({'success': True, 'message': f'Access Granted: Valid ticket for {booking.user.email}'})
        else:
            return JsonResponse({'success': False, 'message': f'Access Denied: Ticket is {booking.status}'})
    else:
        # Regular request
        # 🔒 Admin protection (IMPORTANT)
        if request.user.role != 'admin':
            return redirect('user_dashboard')

        booking = get_object_or_404(Booking, booking_id=booking_uuid)

        # 📅 Optional but strongly recommended — date validation
        if booking.slot.date != timezone.localdate():
            messages.error(request, "Access Denied: Ticket is not for today.")
            return redirect('qr_scanner_page')

        # ✅ Status validation
        if booking.status == 'VALID':
            booking.status = 'USED'
            booking.save()
            messages.success(
                request,
                f"Access Granted: Valid ticket for {booking.user.email}"
            )
        else:
            messages.error(
                request,
                f"Access Denied: Ticket is {booking.status}"
            )

        return redirect('qr_scanner_page')

@login_required
def resolve_sos(request, sos_id):
    if request.user.role != 'admin':
        return redirect('user_dashboard')
        
    sos = get_object_or_404(SOSAlert, id=sos_id)
    sos.status = 'RESOLVED' # Requirement H.6
    sos.save()
    
    messages.success(request, f"Emergency for {sos.user.email} has been marked as Resolved.")
    return redirect('admin_dashboard')

@login_required
def admin_temple_list(request):
    if request.user.role != 'admin':
        return redirect('user_dashboard')
    temples = Temple.objects.all()
    return render(request, 'management/temple_list.html', {'temples': temples})

@login_required
def admin_temple_add(request):
    if request.user.role != 'admin': return redirect('user_dashboard')
    if request.method == 'POST':
        Temple.objects.create(
            name=request.POST.get('name'),
            district=request.POST.get('district'),
            state=request.POST.get('state'),
            deity=request.POST.get('deity'),
            description=request.POST.get('description'),
            image=request.FILES.get('image')
        )
        messages.success(request, "New temple registered successfully.")
        return redirect('admin_temple_list')
    return render(request, 'management/temple_form.html')

@login_required
def admin_temple_edit(request, pk):
    if request.user.role != 'admin': return redirect('user_dashboard')
    temple = get_object_or_404(Temple, pk=pk)
    if request.method == 'POST':
        temple.name = request.POST.get('name')
        temple.district = request.POST.get('district')
        temple.state = request.POST.get('state')
        temple.deity = request.POST.get('deity')
        temple.description = request.POST.get('description')
        if request.FILES.get('image'):
            temple.image = request.FILES.get('image')
        temple.save()
        messages.success(request, f"{temple.name} updated successfully.")
        return redirect('admin_temple_list')
    return render(request, 'management/temple_form.html', {'temple': temple})

@login_required
def admin_temple_delete(request, pk):
    if request.user.role != 'admin': return redirect('user_dashboard')
    temple = get_object_or_404(Temple, pk=pk)
    temple.delete()
    messages.success(request, "Temple removed from registry.")
    return redirect('admin_temple_list')

@login_required
def admin_slot_mgmt(request):
    if request.user.role != 'admin':
        return redirect('user_dashboard')

    slots = DarshanSlot.objects.select_related('temple').all().order_by('-date')

    return render(request, 'management/slot_mgmt.html', {'slots': slots})

@login_required
def admin_slot_add(request):
    if request.user.role != 'admin':
        return redirect('user_dashboard')

    if request.method == 'POST':
        temple = get_object_or_404(Temple, id=request.POST.get('temple'))
        max_cap = int(request.POST.get('max_capacity'))

        DarshanSlot.objects.create(
            temple=temple,
            date=request.POST.get('date'),
            slot_type=request.POST.get('slot_type'),
            max_capacity=max_cap,
            reserved_count=0  # ✅ FIXED (do NOT touch available_tickets)
        )

        messages.success(request, "New darshan session scheduled.")
        return redirect('admin_slot_mgmt')

    return render(request, 'management/slot_form.html', {
        'temples': Temple.objects.all()
    })


@login_required
def admin_slot_edit(request, pk):
    if request.user.role != 'admin':
        return redirect('user_dashboard')

    slot = get_object_or_404(DarshanSlot, pk=pk)

    if request.method == 'POST':
        new_max = int(request.POST.get('max_capacity'))

        # ✅ how many already booked
        already_booked = slot.reserved_count

        # 🚫 prevent shrinking below booked count
        if new_max < already_booked:
            messages.error(
                request,
                f"Capacity cannot be less than already booked ({already_booked})."
            )
            return redirect('admin_slot_mgmt')

        # ✅ safe update
        slot.max_capacity = new_max
        slot.date = request.POST.get('date')
        slot.slot_type = request.POST.get('slot_type')
        slot.save()

        messages.success(request, "Session capacity updated.")
        return redirect('admin_slot_mgmt')

    return render(request, 'management/slot_form.html', {
        'slot': slot,
        'temples': Temple.objects.all()
    })


from django.http import JsonResponse

@login_required
def admin_live_stats(request):
    if request.user.role != 'admin':
        return JsonResponse({"error": "unauthorized"}, status=403)

    return JsonResponse({
        "used_bookings": Booking.objects.filter(status='USED').count(),
        "total_users": Booking.objects.aggregate(total=Sum('ticket_count'))['total'] or 0,
        "active_sos": SOSAlert.objects.filter(status='PENDING').count(),
        "total_dakshan": Contribution.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
    })


@login_required
def admin_slot_delete(request, pk):
    if request.user.role != 'admin': return redirect('user_dashboard')
    slot = get_object_or_404(DarshanSlot, pk=pk)
    slot.delete()
    messages.success(request, "Darshan session removed.")
    return redirect('admin_slot_mgmt')

@login_required
def admin_sos_monitor(request):
    if request.user.role != 'admin':
        return redirect('user_dashboard')
    alerts = SOSAlert.objects.all().order_by('-created_at')
    return render(request, 'management/sos_monitor.html', {'alerts': alerts})

@login_required
def admin_finance(request):
    if request.user.role != 'admin':
        return redirect('user_dashboard')
    contributions = Contribution.objects.all().order_by('-timestamp')
    total_dakshan = contributions.aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'management/finance_report.html', {
        'contributions': contributions,
        'total_dakshan': total_dakshan
    })

