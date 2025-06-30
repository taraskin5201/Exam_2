
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm
from .forms import WorkForm
from .models import Work
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .models import Comment
from .forms import CommentForm
from django.db.models import Count, Avg
from .models import Rating
from .forms import RatingForm
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Реєстрація успішна! Увійдіть у свій акаунт.')
            return redirect('login')
        else:
            messages.error(request, 'Помилка при реєстрації. Перевірте форму.')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})



@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль успішно оновлено!')
            return redirect('edit_profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def create_work(request):
    if request.method == 'POST':
        form = WorkForm(request.POST)
        if form.is_valid():
            work = form.save(commit=False)
            work.author = request.user
            work.save()
            messages.success(request, 'Твір опубліковано успішно!')
            return redirect('work_detail', pk=work.pk)
    else:
        form = WorkForm()
    return render(request, 'accounts/create_work.html', {'form': form})


def work_list(request):
    sort = request.GET.get('sort')
    genre = request.GET.get('genre')

    work_list = Work.objects.all().annotate(
        comment_count=Count('comments'),
        avg_rating=Avg('ratings__value')
    )

    if genre:
        work_list = work_list.filter(genre=genre)

    if sort == 'rating':
        work_list = work_list.order_by('-avg_rating')
    elif sort == 'comments':
        work_list = work_list.order_by('-comment_count')
    else:
        work_list = work_list.order_by('-published_at')

    paginator = Paginator(work_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    genres = Work.objects.values_list('genre', flat=True).distinct()

    return render(request, 'accounts/work_list.html', {
        'page_obj': page_obj,
        'genres': genres,
        'current_genre': genre,
        'current_sort': sort,
    })

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.works.update(author=None)
        user.comment_set.update(user=None)
        user.delete()
        logout(request)
        messages.success(request, 'Ваш акаунт було успішно видалено.')
        return redirect('login')
    return render(request, 'accounts/delete_account_confirm.html')


def edit_work(request, pk):
    work = get_object_or_404(Work, pk=pk)
    if request.user != work.author:
        return redirect('work_detail', pk=pk)

    if request.method == "POST":
        form = WorkForm(request.POST, instance=work)
        if form.is_valid():
            form.save()
            return redirect('work_detail', pk=work.pk)
    else:
        form = WorkForm(instance=work)

    return render(request, 'accounts/edit_work.html', {'form': form, 'work': work})

@login_required
def delete_work(request, work_id):
    work = get_object_or_404(Work, pk=work_id)

    if request.user != work.author:
        return redirect('work_detail', pk=work_id)

    if request.method == 'POST':
        work.delete()
        return redirect('work_list')

    return redirect('edit_work', work_id=work_id)

def work_detail(request, pk):
    work = get_object_or_404(Work, pk=pk)

    content_pages = Paginator(
        [work.content[i:i+1000] for i in range(0, len(work.content), 1000)],
        1
    )
    page_number = request.GET.get('page')
    page_obj = content_pages.get_page(page_number)

    if request.method == 'POST':
        if request.user.is_authenticated:
            if 'comment_submit' in request.POST:
                form = CommentForm(request.POST)
                rating_form = RatingForm()
                if form.is_valid():
                    comment = form.save(commit=False)
                    comment.user = request.user
                    comment.work = work
                    comment.save()
                    print(f'Comment saved: {comment.content}')
                    return redirect('work_detail', pk=work.pk)
                else:
                    print(form.errors)
            elif 'rating_submit' in request.POST:
                rating_form = RatingForm(request.POST)
                form = CommentForm()
                if rating_form.is_valid():
                    rating, created = Rating.objects.update_or_create(
                        user=request.user,
                        work=work,
                        defaults={'value': rating_form.cleaned_data['value']}
                    )
                    return redirect('work_detail', pk=work.pk)
            else:
                form = CommentForm()
                rating_form = RatingForm()
        else:
            form = CommentForm()
            rating_form = RatingForm()
    else:
        form = CommentForm()
        rating_form = RatingForm()

    comments = work.comments.order_by('-created_at')
    avg_rating = work.ratings.aggregate(Avg('value'))['value__avg']

    return render(request, 'accounts/work_detail.html', {
        'work': work,
        'page_obj': page_obj,
        'form': form,
        'rating_form': rating_form,
        'avg_rating': avg_rating,
        'comments': comments,
    })


def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def custom_403(request, exception):
    return render(request, '403.html', status=403)


