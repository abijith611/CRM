#ctrl+k   ctrl+0 to close all methods
from django.core.mail import EmailMessage
import smtplib, ssl
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from re import template
import re
import nltk
# nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
cv = CountVectorizer(max_features=1500)
from unicodedata import category
from urllib import request
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.http import HttpResponse
from django.urls import reverse
from matplotlib.style import context
from .models import Agent, Feedback, Lead, Category
from .forms import (
    LeadForm, 
    LeadModelForm, 
    CustomUserCreationForm, 
    AssignAgentForm, 
    LeadCategoryUpdateForm,
    CategoryModelForm,
    FeedbackModelForm)

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import generic
from agents.mixins import OrganiserAndLoginRequiredMixin






def getSentiment(string1):
    # Natural Language Processing
    # Importing the dataset
    dataset = pd.read_csv('Restaurant_Reviews.tsv', delimiter = '\t', quoting = 3)

    # Cleaning the texts
    
    def getCorpus(string1):
        corpus1 = []
        string = re.sub('[^a-zA-Z]', ' ', string1).lower().split()
        ps = PorterStemmer()
        all_stopwords = stopwords.words('english')
        all_stopwords.remove('not')
        string = [ps.stem(word) for word in string if not word in set(all_stopwords)]
        string = ' '.join(string)
        return string
    corpus = []
    for i in range(0, 1000):
        corpus.append(getCorpus(dataset['Review'][i]))
    corpus.append(getCorpus(string1))

    # Creating the Bag of Words model

    X = cv.fit_transform(corpus).toarray()
    predict_array=X[-1]
    X=np.delete(X,-1,axis=0)
    y = dataset.iloc[:, -1].values


    # Splitting the dataset into the Training set and Test set
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.20, random_state = 0)

    # Training the Naive Bayes model on the Training set
    from sklearn.svm import SVC
    classifier = SVC( kernel = 'linear' ,random_state= 0)
    classifier.fit(X_train, y_train)

    # Predicting the Test set results
    y_pred = classifier.predict(X_test)
    prediction = classifier.predict([predict_array])
    if prediction == 0:
        print("negative")
        return 0
    elif prediction == 1:
        print("positive")
        return 1
    # print("concatenate: ",np.concatenate((y_pred.reshape(len(y_pred),1), y_test.reshape(len(y_test),1)),1))

    # Making the Confusion Matrix
    # from sklearn.metrics import confusion_matrix, accuracy_score
    # cm = confusion_matrix(y_test, y_pred)
    # print("confusion matrix: ",cm)
    # "accuracy score: ",accuracy_score(y_test, y_pred)






class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")


class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_list.html"
    context_object_name = "leads"
    def get_queryset(self):
        user = self.request.user
        #initial queryset of leads for entire organisation
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile, 
            agent__isnull= False)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation, 
            agent__isnull= False)
            #filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset
    
    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(LeadListView, self).get_context_data(**kwargs)
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile, 
            agent__isnull=True)
            context.update({
                "unassigned_leads": queryset
            })
        return context

def landing_page(request):
    return render(request, "landing.html")

def lead_list(request):
    leads = Lead.objects.all()
    context = {
        "leads" : leads
    }
    return render(request, "leads/lead_list.html", context)

class LeadDetailView(LoginRequiredMixin,generic.DetailView):
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"

    def get_queryset(self):
        user = self.request.user
        #initial queryset of leads for entire organisation
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            #filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset

def lead_detail(request, pk):
    lead = Lead.objects.get(id = pk)
    context = { "lead" : lead}
    return render(request, "leads/lead_detail.html", context)

class LeadCreateView(OrganiserAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm
    def get_success_url(self):
        return reverse("leads:lead-list")
    def form_valid(self, form):
        recipient_list1=[]
        lead = form.save(commit=False)
        if(lead.agent!=None):
            recipient_list1.append(lead.agent.getEmail())
        #print(lead.agent.getEmail())
        lead.organisation = self.request.user.userprofile
        lead.save()
        send_mail(
            subject="A lead has been created",
            message="Go to the site to see the new lead", 
            from_email="test@test.com", 
            recipient_list = recipient_list1)
        return super(LeadCreateView, self).form_valid(form)
        

def lead_create(request):
    form = LeadModelForm()
    if request.method == "POST":
        print('receiving a post request')
        form = LeadModelForm(request.POST)
        if form.is_valid():
            print("the form is valid")
            form.save()
            print("The lead has been added")
            return redirect("/leads")
    context = {
    "form" : form
    }
    return render(request, "leads/lead_create.html", context)


class LeadUpdateView(OrganiserAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm

    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.userprofile)

    def get_success_url(self):
        return reverse("leads:lead-list")

def lead_update(request, pk):
    lead = Lead.objects.get(id = pk)
    form = LeadModelForm(instance=lead)
    if request.method == "POST":
        print('receiving a post request')
        form = LeadModelForm(request.POST, instance= lead)
        if form.is_valid():
            print("the form is valid")
            form.save()
            print("The lead has been added")
            return redirect("/leads")
    context = {
    "form" : form,
    "lead": lead
    }
    return render(request, "leads/lead_update.html", context)

class LeadDeleteView(OrganiserAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/lead_delete.html"
    form_class = LeadModelForm
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.userprofile)
        
    def get_success_url(self):
        return reverse("leads:lead-list")

def lead_delete(request, pk):
    lead = Lead.objects.get(id = pk)
    lead.delete()
    return redirect("/leads")


class AssignAgentView(OrganiserAndLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request":self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id = self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)

        context.update({
            "unassigned_lead_count": queryset.filter(category__isnull = True).count(),
            "queryset" : queryset,
            "category": category
        })
        return context

    def get_queryset(self):
        user = self.request.user
        #initial queryset of leads for entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
    
        return queryset


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"



    def get_queryset(self):
        user = self.request.user
        #initial queryset of leads for entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
    
        return queryset

class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm
    # print("category: ",Lead.objects.filter(category = "converted"))

    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            #filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk": self.get_object().id})

    def form_valid(self, form):
        # print(self.get_object().category)
        if(self.get_object().category!=None):
            category_object_lead = Category.objects.get(name = self.get_object().category)
            count0 = category_object_lead.total_count - 1
            Category.objects.filter(name = self.get_object().category).update(total_count=count0)
        category = form.cleaned_data["category"]
        # print(category)
        category_object = Category.objects.get(name = category)
        count1 = category_object.total_count + 1
        # print(count1)
        Category.objects.filter(name = category).update(total_count=count1)
        return super(LeadCategoryUpdateView, self).form_valid(form)





class CategoryUpdateView(OrganiserAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/category_update.html"
    form_class = CategoryModelForm
    def get_success_url(self):
        return reverse("leads:category-list")
    def get_queryset(self):
        user = self.request.user
        #initial queryset of leads for entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
    
        return queryset


class CategoryCreateView(OrganiserAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/category_create.html"
    form_class = CategoryModelForm
    def get_success_url(self):
        return reverse("leads:category-list")
    def form_valid(self, form):
        category = form.save(commit=False)
        category.organisation = self.request.user.userprofile
        category.save()
        return super(CategoryCreateView, self).form_valid(form)

class CategoryDeleteView(OrganiserAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/category_delete.html"
    def get_success_url(self):
        return reverse("leads:category-list")
    def get_queryset(self):
        user = self.request.user
        #initial queryset of leads for entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
    
        return queryset

class FeedbackCreateView(AccessMixin, generic.CreateView):
    template_name = "leads/feedback_create.html"
    form_class = FeedbackModelForm
    def get_success_url(self):
        # print("success")
        return reverse('landing-page')
    def form_valid(self, form):
        # print("in form valid")
        feedback = form.save(commit = False)
        feedback.sentiment_value=getSentiment(form.cleaned_data["feedback"])
        feedback.save()
        return super(FeedbackCreateView, self).form_valid(form)





class FeedbackListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/feedback_list.html"
    context_object_name = "feedback_list"
    # print("feedback list view")
    def get_queryset(self):
        # print(Feedback.objects.filter(sentiment_value = 1))
        queryset = Feedback.objects.filter(sentiment_value = 0)
        # print(queryset)
        return queryset

class FeedbackNotifyView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/feedback_notify.html"
    context_object_name = "feedback"
    model = Feedback
    
    def get_context_data(self, **kwargs):
        context = super(FeedbackNotifyView, self).get_context_data(**kwargs)
        # print("email: ",self.object.email)
        context['email'] = self.object.email
        # context.update({
        #     "email" : self.object.email
        # })

        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = "***REMOVED***"
        password = "***REMOVED***"
        context1 = ssl.create_default_context()
        server = smtplib.SMTP(smtp_server, port)
        
        try:
            server.ehlo()
            server.starttls(context=context1)
            server.login(sender_email,password)
            message = "\n your feedback is noted by the agent: "+self.request.user.username
            server.sendmail(sender_email, self.object.email, msg = message)
            self.object.is_read = True
            self.object.save()
        except Exception as e:
            print(e)
        finally:
            server.quit()
        
        return context
    
    def get_queryset(self):
        # print(Feedback.objects.filter(sentiment_value = 1))
        queryset = Feedback.objects.filter(sentiment_value = 0)
        # print(queryset)
        return queryset
    

class FeedbackDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "leads/feedback_delete.html"

    def get_queryset(self):
        # print(Feedback.objects.filter(sentiment_value = 1))
        queryset = Feedback.objects.filter(sentiment_value = 0)
        # print(queryset)
        return queryset

    def get_success_url(self):
        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = "***REMOVED***"
        password = "***REMOVED***"
        context1 = ssl.create_default_context()
        server = smtplib.SMTP(smtp_server, port)
        
        try:
            server.ehlo()
            server.starttls(context=context1)
            server.login(sender_email,password)
            message = "\n your feedback is deleted by the agent: " +self.request.user.username
            server.sendmail(sender_email, self.object.email, msg = message)
            self.object.is_read = True
            self.object.save()
        except Exception as e:
            print(e)
        finally:
            server.quit()

        # email.send()
        return reverse("leads:complaints")