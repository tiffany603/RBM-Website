# Create your views here.
import numpy as np
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django import forms
from rbm_website.apps.rbm.models import DBNModel

class DBNListView(ListView):
    model = DBNModel

class DBNDetailView(DetailView):
    model = DBNModel


class DBNForm(forms.Form):
    name =  forms.CharField(max_length=200)
    description = forms.CharField(max_length=1000, widget=forms.Textarea)
    height = forms.IntegerField(initial=28)
    width = forms.IntegerField(initial=28)
    labels = forms.IntegerField()
    learning_rate = forms.FloatField()
    layer_count = forms.IntegerField(widget = forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        layers = kwargs.pop('layer', 0)

        super(DBNForm, self).__init__(*args, **kwargs)
        self.fields['layer_count'].initial = layers

        for index in range(int(layers)):
            self.fields['layer_{index}'.format(index=index)] = forms.IntegerField()

    def clean_height(self):
        data = self.cleaned_data['height']
        if (not(0 < data <= 30)):
            raise forms.ValidationError("Height must be a positive integer, maximum of 30!")
        return data

    def clean_width(self):
        data = self.cleaned_data['width']
        if (not(0 < data <= 30)):
            raise forms.ValidationError("Width must be a positive integer, maximum of 30!")
        return data

    def clean_labels(self):
        data = self.cleaned_data['labels']
        if (data <= 0):
            raise forms.ValidationError("Labels must be a positive integer!")
        return data

    def clean_learning_rate(self):
        data = self.cleaned_data['learning_rate']
        if (data <= 0):
            raise forms.ValidationError("Learning rate must be a positive float!")
        return data

def train(request, dbn_id):
    if request.method == 'POST':
        print request
        dbn = get_object_or_404(DBNModel , pk=dbn_id)
        print request.POST['test']
        return render(request, 'rbm/training.html', {})
    else:
        dbn = get_object_or_404(DBNModel , pk=dbn_id)
        return render(request, 'rbm/train.html', {'dbn': dbn})

def training(request):
    return render(request, 'rbm/training.html', {})

def create(request):
    if request.method == 'POST':
        form = DBNForm(request.POST, layer=request.POST.get('layer_count'))

        if form.is_valid():
            height = form.cleaned_data['height']
            width = form.cleaned_data['width']
            visible = height*width
            labels = form.cleaned_data['labels']
            learning_rate = form.cleaned_data['learning_rate']
            description = form.cleaned_data['description']
            name = form.cleaned_data['name']
            creator = request.user.username
            layer_count = form.cleaned_data['layer_count']

            topology = []
            topology.append(visible)
            for index in range(layer_count):
                topology.append(form.cleaned_data['layer_{index}'.format(index=index)])

            dbn = DBNModel.build_dbn(name, creator, description, height, width, topology, labels, learning_rate)
            dbn.save()
            messages.add_message(request, messages.INFO, 'Successfully created the DBN!')
            return redirect('index')

    else:
        form = DBNForm()

    return render(request, 'rbm/create.html', { 'form' : form })

def regenerate(request, dbn_id):
    dbn = get_object_or_404(DBNModel , pk=dbn_id)
    data = [map(int, request.POST['data'].split(','))]
    (visible_state, hidden_state) = dbn.regenerate(data)
    visible_state = np.array_str(visible_state)
    hidden_state = np.array_str(hidden_state)
    return render(request, 'rbm/regenerate.html', {'old_data': request.POST['data'], 'dbn': dbn, 'visible_state': visible_state, 'hidden_state': hidden_state})

