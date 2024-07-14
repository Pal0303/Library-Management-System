from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, JsonResponse
from . import forms, models
from django.contrib.auth.models import Group
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime, timedelta, date
from django.core.mail import send_mail
from librarymanagement.settings import EMAIL_HOST_USER
import requests



# Existing views...

def search_books(request):
    search_results = []
    query = request.GET.get('query')
    if query:
        url = "https://googlebooksraygorodskijv1.p.rapidapi.com/addVolumeToBookshelf"
        payload = {
            # Assuming the query parameter is passed in the request
            "query": query
        }
        headers = {
            "x-rapidapi-key": "4c0e7da09dmsh88cfe402653dd8cp180268jsnf2710a4a4e2c",
            "x-rapidapi-host": "GoogleBooksraygorodskijV1.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers, params=payload)
        if response.status_code == 200:
            search_results = response.json().get('items', [])
    
    return render(request, 'library/index.html', {'search_results': search_results})

# Other existing views...
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'library/index.html')

# For showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'library/studentclick.html')

# For showing signup/login button for admin
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'library/adminclick.html')

def studentsignup_view(request):
    form1 = forms.StudentUserForm()
    form2 = forms.StudentExtraForm()
    mydict = {'form1': form1, 'form2': form2}
    if request.method == 'POST':
        form1 = forms.StudentUserForm(request.POST)
        form2 = forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user = form1.save()
            user.set_password(user.password)
            user.save()
            f2 = form2.save(commit=False)
            f2.user = user
            user2 = f2.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)

        return HttpResponseRedirect('studentlogin')
    return render(request, 'library/studentsignup.html', context=mydict)

def is_admin(user):
    return user.is_superuser or user.is_staff

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

def afterlogin_view(request):
    if is_admin(request.user):
        return render(request, 'library/adminafterlogin.html')
    elif is_student(request.user):
        return render(request, 'library/studentafterlogin.html')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def addbook_view(request):
    form = forms.BookForm()
    if request.method == 'POST':
        form = forms.BookForm(request.POST)
        if form.is_valid():
            user = form.save()
            return render(request, 'library/bookadded.html')
    return render(request, 'library/addbook.html', {'form': form})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewbook_view(request):
    books = models.Book.objects.all()
    return render(request, 'library/viewbook.html', {'books': books})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def issuebook_view(request):
    form = forms.IssuedBookForm()
    if request.method == 'POST':
        form = forms.IssuedBookForm(request.POST)
        if form.is_valid():
            obj = models.IssuedBook()
            obj.enrollment = request.POST.get('enrollment2')
            obj.isbn = request.POST.get('isbn2')
            obj.save()
            return render(request, 'library/bookissued.html')
    return render(request, 'library/issuebook.html', {'form': form})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewissuedbook_view(request):
    issuedbooks = models.IssuedBook.objects.all()
    li = []
    for ib in issuedbooks:
        issdate = str(ib.issuedate.day) + '-' + str(ib.issuedate.month) + '-' + str(ib.issuedate.year)
        expdate = str(ib.expirydate.day) + '-' + str(ib.expirydate.month) + '-' + str(ib.expirydate.year)
        # Fine calculation
        days = (date.today() - ib.issuedate).days
        fine = max(0, (days - 15) * 10)

        books = list(models.Book.objects.filter(isbn=ib.isbn))
        students = list(models.StudentExtra.objects.filter(enrollment=ib.enrollment))
        for i, book in enumerate(books):
            t = (students[i].get_name, students[i].enrollment, book.name, book.author, issdate, expdate, fine, ib.status)
            li.append(t)

    return render(request, 'library/viewissuedbook.html', {'li': li})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewstudent_view(request):
    students = models.StudentExtra.objects.all()
    return render(request, 'library/viewstudent.html', {'students': students})

@login_required(login_url='studentlogin')
def viewissuedbookbystudent(request):
    student = models.StudentExtra.objects.filter(user_id=request.user.id)
    issuedbook = models.IssuedBook.objects.filter(enrollment=student[0].enrollment)

    li1 = []
    li2 = []
    for ib in issuedbook:
        books = models.Book.objects.filter(isbn=ib.isbn)
        for book in books:
            t = (request.user, student[0].enrollment, student[0].branch, book.name, book.author)
            li1.append(t)
        issdate = str(ib.issuedate.day) + '-' + str(ib.issuedate.month) + '-' + str(ib.issuedate.year)
        expdate = str(ib.expirydate.day) + '-' + str(ib.expirydate.month) + '-' + str(ib.expirydate.year)
        # Fine calculation
        days = (date.today() - ib.issuedate).days
        fine = max(0, (days - 15) * 10)
        t = (issdate, expdate, fine, ib.status, ib.id)
        li2.append(t)

    return render(request, 'library/viewissuedbookbystudent.html', {'li1': li1, 'li2': li2})

def returnbook(request, id):
    issued_book = models.IssuedBook.objects.get(pk=id)
    issued_book.status = "Returned"
    issued_book.save()
    return redirect('viewissuedbookbystudent')

def aboutus_view(request):
    return render(request, 'library/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name = sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(f'{name} || {email}', message, EMAIL_HOST_USER, ['wapka1503@gmail.com'], fail_silently=False)
            return render(request, 'library/contactussuccess.html')
    return render(request, 'library/contactus.html', {'form': sub})

def add_volume_to_bookshelf(request):
    url = "https://googlebooksraygorodskijv1.p.rapidapi.com/addVolumeToBookshelf"

    payload = "-----011000010111000001101001--\r\n\r\n"
    headers = {
        "x-rapidapi-key": "4c0e7da09dmsh88cfe402653dd8cp180268jsnf2710a4a4e2c",
        "x-rapidapi-host": "GoogleBooksraygorodskijV1.p.rapidapi.com",
        "Content-Type": "multipart/form-data; boundary=---011000010111000001101001"
    }

    response = requests.post(url, data=payload, headers=headers)

    try:
        response_data = response.json()
    except ValueError:
        response_data = {'error': 'Failed to parse JSON response'}

    return JsonResponse(response_data)
