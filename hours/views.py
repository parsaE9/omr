import jdatetime
from datetime import datetime
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.dateparse import parse_duration
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Trunc
from django.core.mail import send_mail
from hours.models import *
from hours.persian import normalize_digits, persian_numbers, get_weekday_count, get_days_count


class EmployeeHours(DetailView):
    model = User
    template_name = 'hours/employee_hours.html'

    def get_object(self, **kwargs):
        if self.kwargs.get('employee'):
            return get_object_or_404(User, username=self.kwargs.get('employee'))
        print("USER = ")
        print(self.request.user)
        return self.request.user

    def get_context_data(self, **kwargs):
        print("USER = ")
        print(self.request.user)
        organization = get_object_or_404(Organization, slug=self.kwargs.get('slug'))
        context = super(EmployeeHours, self).get_context_data(**kwargs)
        context['organization'] = organization
        context['works'] = self.object.work_set.filter(organization=context['organization']).select_related(
            'project').order_by('-date', '-id')
        context['today'] = jdatetime.date.today().strftime('%Y/%m/%d')
        context['is_admin'] = self.request.user == organization.admin
        context['next'] = '/{}/{}'.format(organization.slug,
                                          self.kwargs.get('employee', ''))

        if self.request.user not in organization.employees.all():
            if self.request.user.email in organization.invitations:
                organization.employees.add(self.request.user)
            else:
                raise PermissionDenied

        return context


class EmployeeNotes(DetailView):
    model = User
    template_name = 'hours/employee_notes.html'

    def get_object(self, **kwargs):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(EmployeeNotes, self).get_context_data(**kwargs)
        context['organization'] = get_object_or_404(Organization, slug=self.kwargs.get('slug'))
        context['is_admin'] = self.request.user == context['organization'].admin
        notes = self.object.note_set if not context['is_admin'] else Note.objects.all()
        context['notes'] = notes.filter(organization=context['organization']).order_by('-date', '-id')
        # context['today'] = jdatetime.date.today().strftime('%Y/%m/%d')

        if self.request.user not in context['organization'].employees.all():
            raise PermissionDenied

        return context


class OrganizationHours(DetailView):
    model = Organization
    template_name = 'hours/organization_hours.html'

    def get_context_data(self, **kwargs):
        context = super(OrganizationHours, self).get_context_data(**kwargs)
        context['organization'] = get_object_or_404(
            Organization, slug=self.kwargs.get('slug'))
        context['works'] = context['organization'].work_set.all().select_related(
            'project', 'employee').order_by('-date', '-id')[:100]
        # context['today'] = jdatetime.date.today().strftime('%Y/%m/%d')

        if self.request.user != context['organization'].admin:
            raise PermissionDenied
        return context


class OrganizationStats(DetailView):
    model = Organization
    my_dictionary = {}

    # form = ChartDateForm()

    def get_context_data(self, **kwargs):
        context = super(OrganizationStats, self).get_context_data(**kwargs)
        print("--------------")
        print(kwargs)
        print("get_context_data POST = {} ".format(self.request.POST))
        print("dictionary is : {}".format(self.my_dictionary))

        context['today'] = jdatetime.date.today().strftime('%Y/%m/%d')
        if self.request.user not in self.object.employees.all():
            raise PermissionDenied

        context['is_admin'] = self.request.user == self.object.admin

        def format_durations(items):
            items = list(items)
            for item in items:
                item['duration'] = time_format(item['duration'])
            return items

        # TODO BEGIN
        gregorian_date_source = ''
        gregorian_date_end = ''

        if self.my_dictionary.get('date-source') and self.my_dictionary.get('date-end'):
            split_source = self.my_dictionary['date-source'].split('/')
            split_end = self.my_dictionary['date-end'].split('/')
            source = jdatetime.jalali.JalaliToGregorian(int(split_source[0]), int(split_source[1]),
                                                        int(split_source[2]))
            gregorian_date_source = str(source.gyear) + "-" + str(source.gmonth) + "-" + str(source.gday)
            end = jdatetime.jalali.JalaliToGregorian(int(split_end[0]), int(split_end[1]), int(split_end[2]))
            gregorian_date_end = str(end.gyear) + "-" + str(end.gmonth) + "-" + str(end.gday)
            context['works'] = Work.objects.filter(organization=self.object,
                                                   date__range=[gregorian_date_source, gregorian_date_end])
            context['hours'] = self.object.work_set.filter(organization=context['organization'],
                                                           date__range=[gregorian_date_source,
                                                                        gregorian_date_end]).select_related(
                'project').order_by('-date', '-id')
            context['date_source'] = self.my_dictionary['date-source']
            context['date_end'] = self.my_dictionary['date-end']

        else:
            context['works'] = Work.objects.filter(organization=self.object)
            context['hours'] = self.object.work_set.filter(organization=context['organization']).select_related(
                'project').order_by('-date', '-id')

            context['date_source'] = "1399/01/01"
            context['date_end'] = context['today']

        if not context['is_admin']:
            context['works'] = context['works'].filter(employee=self.request.user)
            context['hours'] = context['hours'].filter(employee=self.request.user)

        if context['is_admin']:
            context['employees'] = format_durations(
                Work.objects.filter(organization=self.object, employee__is_active=True).
                    values('employee__last_name', 'employee__username').annotate(duration=Sum('duration')).order_by(
                    'employee'))

            # TODO

            context['employee_names'] = context['employees']
            context['is_selected'] = False
            last_name = self.my_dictionary.get('employee_select')

            if last_name and last_name != 'همه':
                context['works'] = context['works'].filter(employee__last_name=last_name)
                context['hours'] = context['hours'].filter(employee__last_name=last_name)
                context['employee_names'] = format_durations(
                    Work.objects.filter(organization=self.object, employee__is_active=True,
                                        employee__last_name=last_name, date__range=[gregorian_date_source,
                                                                                    gregorian_date_end]).
                        values('employee__last_name', 'employee__username').annotate(duration=Sum('duration')).order_by(
                        'employee'))
                context['is_selected'] = True
                fridays_count = get_weekday_count(gregorian_date_source, gregorian_date_end, 'friday')
                thursdays_count = get_weekday_count(gregorian_date_source, gregorian_date_end, 'thursday')
                context['weekends'] = fridays_count + thursdays_count
                all_days_count = get_days_count(gregorian_date_source, gregorian_date_end)
                context['holidays'] = Holiday.objects.filter(date__range=[gregorian_date_source, gregorian_date_end])
                context['total_off_days'] = context['weekends'] + len(context['holidays'].filter(is_weekend=False))
                context['miss_days'] = all_days_count - context['total_off_days'] - len(context['hours'])
                # TODO END

        context['data'] = context['works'].values('project__title').annotate(date=Trunc('date', 'day'),
                                                                             duration=Sum('duration')).order_by('date')
        context['works'] = context['works'].values('project__title', 'project__color').annotate(
            duration=Sum('duration')).order_by('project')
        chart_data = {}
        for item in context['data']:
            jalali = jalali_date(item['date']).strftime('%b %y')

            key = str(item['project__title']) + jalali
            if key not in chart_data:
                chart_data[key] = {
                    'title': item['project__title'],
                    'date': jalali,
                    'duration': item['duration'].seconds
                }
            else:
                chart_data[key]['duration'] += item['duration'].seconds

        context['data'] = list(chart_data.values())
        context['works'] = format_durations(context['works'])

        self.my_dictionary['date-source'] = ''
        self.my_dictionary['date-end'] = ''
        self.my_dictionary['employee_select'] = ''

        return context

    def post(self, request, *args, **kwargs):
        print(f"post POST = {self.request.POST}")
        self.my_dictionary['date-source'] = self.request.POST.get('date-source')
        self.my_dictionary['date-end'] = self.request.POST.get('date-end')
        self.my_dictionary['employee_select'] = self.request.POST.get('employee_select')
        # if self.my_dictionary.get('employee_select') and self.my_dictionary.get('employee_select') != 'همه':
        print("my dictionary = {}".format(self.my_dictionary))
        print("POST = {}".format(self.request.POST))
        print("self.my_dictionary['employee_select'] = {}".format(self.my_dictionary.get('employee_select')))
        return HttpResponseRedirect('./stats')


class UserDetail(DetailView):
    model = User
    template_name = 'hours/user_detail.html'

    def get_object(self, **kwargs):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(UserDetail, self).get_context_data(**kwargs)
        context['organizations'] = self.object.organization_set.all()
        return context


class CalendarView(DetailView):
    model = Holiday
    template_name = 'hours/calendar.html'

    def get_object(self, **kwargs):
        return Holiday.objects.all()

    def get_context_data(self, **kwargs):
        context = super(CalendarView, self).get_context_data(**kwargs)
        context['today'] = datetime.today().strftime('%Y-%m-%d')
        return context

    def post(self, request, *args, **kwargs):
        date = self.request.POST['gregorian-date']
        if get_weekday_count(date, date, 'friday') or get_weekday_count(date, date, 'thursday'):
            Holiday(date=date, description=self.request.POST['description'], is_weekend=True).save()
        else:
            Holiday(date=date, description=self.request.POST['description']).save()
        return HttpResponseRedirect('./calendar')


class WorkForm(forms.ModelForm):
    class Meta:
        model = Work
        exclude = []

    def is_valid(self):
        try:
            self.data._mutable = True
            self.data['date'] = jdatetime.date(
                *map(int, normalize_digits(self.data['date']).split('/'))).togregorian().strftime('%Y-%m-%d')
            self.data['duration'] = normalize_digits(
                self.data['duration']) + ':00'
        except:
            pass

        return super(WorkForm, self).is_valid()


class WorkCreate(CreateView):
    model = Work
    form_class = WorkForm
    template_name = '403.html'

    def form_valid(self, form):
        work = form.save(commit=False)

        if self.request.user != work.employee and self.request.user != work.organization.admin:
            raise PermissionDenied

        work.save()
        self.success_url = self.request.GET.get('next')
        return super(WorkCreate, self).form_valid(form)


class WorkUpdate(WorkCreate, UpdateView):
    pass


class WorkDelete(DeleteView):
    model = Work

    def get_success_url(self):
        if self.request.user != self.object.employee and self.request.user != self.object.organization.admin:
            raise PermissionDenied

        return self.request.GET.get('next')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = ['content_html']

    def is_valid(self):
        try:
            self.data._mutable = True
            self.data['date'] = jdatetime.date(
                *map(int, normalize_digits(self.data['date']).split('/'))).togregorian().strftime('%Y-%m-%d')
        except:
            pass

        return super(NoteForm, self).is_valid()


class NoteCreate(CreateView):
    model = Note
    form_class = NoteForm

    def form_valid(self, form):
        note = form.save(commit=False)

        if self.request.user != note.organization.admin:
            raise PermissionDenied

        note.save()
        return super(NoteCreate, self).form_valid(form)

    def form_invalid(self, form):
        # todo: set error message
        return redirect(reverse('employee-notes', args=(form.cleaned_data['organization'].slug,)))


class NoteUpdate(NoteCreate, UpdateView):
    pass


class NoteDelete(DeleteView):
    model = Note

    def get_success_url(self):
        if self.request.user != self.object.organization.admin:
            raise PermissionDenied

        return reverse('employee-notes', args=(self.object.organization.slug,))

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


@login_required
def note_email(request, pk):
    note = get_object_or_404(Note, pk=pk)

    if request.user != note.organization.admin:
        raise PermissionDenied

    style = {
        'success': 'color: #3c763d; background-color: #dff0d8;',
        'info': 'color: #31708f; background-color: #d9edf7;',
        'warning': 'color: #8a6d3b; background-color: #fcf8e4;',
        'danger': 'color: #a94442; background-color: #f2dede;',
    }.get(note.category, 'info')

    html = '<div dir="rtl" style="padding:10px 20px; {}"><div style="font-size: 125%;">{}</div><p style="font-size: 95%;">» {}</p></div>'.format(
        style, note.content_html.translate(persian_numbers), note.date_text().translate(persian_numbers))
    text = (note.content + ' - ' + note.date_text()).translate(persian_numbers)

    try:
        successful = send_mail('اطلاع‌رسانی {}'.format(note.organization.title), text, 'عمر <omr@sobhe.ir>',
                               ['{} <{}>'.format(note.employee.last_name, note.employee.email)], html_message=html,
                               fail_silently=True)
        message = 'sent' if successful else 'failed'
    except Exception as e:
        message = str(e)

    return HttpResponse(message)


@login_required
def work_import(request, slug):
    import tablib

    organization = get_object_or_404(Organization, slug=slug)

    if request.method == 'POST':
        items = []
        try:
            csv_input = 'employee, date, duration, project, description\n' + \
                        request.POST.get('items', '')
            items = tablib.Dataset().load(csv_input.encode('utf-8'))
        except Exception as e:
            messages.error(request, 'خطا در قالب داده‌های ورودی: {}'.format(e))

        if items:
            try:

                employees, projects = {}, {}
                with transaction.atomic():
                    for item in items:
                        if item[0] not in employees:
                            employees[item[0]] = User.objects.get(
                                username=item[0])
                        if item[3] and item[3] not in projects:
                            projects[item[3]] = Project.objects.get(
                                organization=organization, title=item[3])
                        Work.objects.create(employee=employees[item[0]], organization=organization, date=item[1],
                                            duration=parse_duration(
                                                item[2]), project=projects.get(item[3]), description=item[4])

            except Exception as e:
                messages.error(
                    request, 'خطا در این ردیف از داده‌ها: <p dir="ltr">{} -> {}</p>'.format(','.join(item), e))
            else:
                messages.success(
                    request, '{} ردیف داده ثبت شد.'.format(len(items)))

    return render(request, 'hours/work_import.html', {'organization': organization})
