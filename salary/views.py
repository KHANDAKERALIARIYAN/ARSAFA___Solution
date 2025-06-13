from django.shortcuts import render
from .forms import SalaryCalculationForm
from employees.models import Employee
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def salary_calculation(request):
    result = None
    employee_info = None
    if request.method == 'POST':
        form = SalaryCalculationForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            present_days = form.cleaned_data['present_days']
            absent_days = form.cleaned_data['absent_days']
            per_day_salary = float(employee.salary) / 30
            deduction = per_day_salary * absent_days
            final_salary = float(employee.salary) - deduction
            result = {
                'name': employee.name,
                'designation': employee.designation,
                'phone': employee.phone,
                'salary': employee.salary,
                'present_days': present_days,
                'absent_days': absent_days,
                'per_day_salary': per_day_salary,
                'deduction': deduction,
                'final_salary': final_salary,
            }
            employee_info = employee
    else:
        form = SalaryCalculationForm()
    return render(request, 'salary/salary_calculation.html', {'form': form, 'result': result, 'employee_info': employee_info})
