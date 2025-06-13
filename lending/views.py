from django.shortcuts import render, get_object_or_404, redirect
from .models import Lending
from .forms import LendingForm
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required

@login_required
def lending_dashboard(request):
    total_lendings = Lending.objects.count()
    active_lendings = Lending.objects.filter(status='active').count()
    total_amount = Lending.objects.aggregate(total=Sum('amount'))['total'] or 0
    outstanding = Lending.objects.filter(status__in=['active', 'overdue']).aggregate(total=Sum('amount'))['total'] or 0
    lendings = Lending.objects.select_related('customer').all().order_by('-start_date')
    context = {
        'total_lendings': total_lendings,
        'active_lendings': active_lendings,
        'total_amount': total_amount,
        'outstanding': outstanding,
        'lendings': lendings,
    }
    return render(request, 'lending/lending_dashboard.html', context)

@login_required
def lending_create(request):
    if request.method == 'POST':
        form = LendingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lending_dashboard')
    else:
        form = LendingForm()
    return render(request, 'lending/lending_form.html', {'form': form})

@login_required
def lending_update(request, pk):
    lending = get_object_or_404(Lending, pk=pk)
    if request.method == 'POST':
        form = LendingForm(request.POST, instance=lending)
        if form.is_valid():
            form.save()
            return redirect('lending_dashboard')
    else:
        form = LendingForm(instance=lending)
    return render(request, 'lending/lending_form.html', {'form': form})

@login_required
def lending_delete(request, pk):
    lending = get_object_or_404(Lending, pk=pk)
    if request.method == 'POST':
        lending.delete()
        return redirect('lending_dashboard')
    return render(request, 'lending/lending_confirm_delete.html', {'lending': lending}) 