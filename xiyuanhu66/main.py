#!/usr/bin/env python

import cgi
import os
import django
import webapp2
import random
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from django.http import HttpResponse




class Category(db.Model):
    name = db.StringProperty()
    user = db.UserProperty()

class Item(db.Model):
    name = db.StringProperty()
    wins = db.IntegerProperty(default=0)
    loses = db.IntegerProperty(default=0)
    category = db.ReferenceProperty(Category, collection_name='items')



class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {
            'url': url,
            'user': user,
            'url_linktext': url_linktext,
        }        
        path = os.path.join(os.path.dirname(__file__),'html/home.html')
        self.response.out.write(template.render(path,template_values))

class Vote(webapp2.RequestHandler):
    def post(self):
        params = self.request.params
        if not params.has_key('category_key'):
            self.redirect('/')
        else:
            user = users.get_current_user()
            category_key = self.request.get("category_key")
            category = db.get(category_key)
            items_list = list(category.items)
            randomlist =[]
            for item in items_list:
                if item.name:
                    randomlist.append(item)
            count=len(randomlist)
            firstIndex = random.randint(0,count-1)
            secondIndex = random.randint(0,count-1)
            while (firstIndex == secondIndex):
                secondIndex = random.randint(0,count-1)
            firstItem = randomlist[firstIndex]
            secondItem = randomlist[secondIndex] 
            template_values = {
                'category': category,
                'user':user,
                'firstItem': firstItem,
                'secondItem': secondItem,
            }
            path = os.path.join(os.path.dirname(__file__),'html/vote.html')
            self.response.out.write(template.render(path,template_values))

class RecordVote(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        category_key = self.request.get("category_key")
        category = db.get(category_key)
        items_list = list(category.items)
        randomlist =[]
        for item in items_list:
            if item.name:
                randomlist.append(item)
        count=len(randomlist)
        firstIndex = random.randint(0,count-1)
        secondIndex = random.randint(0,count-1)
        while (firstIndex == secondIndex):
            secondIndex = random.randint(0,count-1)
        firstItem = randomlist[firstIndex]
        secondItem = randomlist[secondIndex] 
            
        params = self.request.params
        if params['recordVote'] == 'Vote':
            if not params.has_key('win_lose'):
                self.redirect('/')
            else:
                items = self.request.get("win_lose")
                items = items.split('/')
                itemWin = Item()
                itemLose = Item()
                for item in randomlist:
                    if (item.name == items[0]):
                        item.wins += 1
                        itemWin = item 
                    elif (item.name == items[1]):
                        item.loses += 1
                        itemLose = item
                itemWin.put()
                itemLose.put()
                template_values = {
                    'user': user,
                    'category': category,
                    'itemWin': itemWin,
                    'itemLose': itemLose,
                    'firstItem': firstItem,
                    'secondItem': secondItem,
                }
                path = os.path.join(os.path.dirname(__file__),'html/recordVote.html')
                self.response.out.write(template.render(path,template_values))

        elif params['recordVote'] == 'Skip':
            template_values = {
                'user': user,
                'category': category,
                'firstItem': firstItem,
                'secondItem': secondItem,
            }
            path = os.path.join(os.path.dirname(__file__),'html/vote.html')
            self.response.out.write(template.render(path,template_values))
                
            

class Result(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        item = users.get_current_user()
        category_key = self.request.get("category_key")
        category = db.get(category_key)

        template_values = {
            'user': user,
            'category': category,
            'items':category.items,
        }
        path = os.path.join(os.path.dirname(__file__),'html/result.html')
        self.response.out.write(template.render(path,template_values))

class AddCategory(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        old_categorys = Category(name="",user=user)
        old_categorys = db.GqlQuery("SELECT * FROM Category WHERE user = :1", user)
        add_category = Category(name="",user=user)
        add_category.name = self.request.get('categoryToAdd')
        if( add_category.name ):
            add_category.put()
    
        template_values = {
            'category': add_category,
            'old_categorys': old_categorys,
            'user': user,
        }
        path = os.path.join(os.path.dirname(__file__),'html/addCategory.html')
        self.response.out.write(template.render(path,template_values))

class EditCategory(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        editedCategory_key = self.request.get("editedCategory")
        params = self.request.params
        editCategory = db.get(editedCategory_key)
        if params['submit'] == 'Delete':        
            editCategory.delete()
        elif params['submit'] == 'Edit':
            content = self.request.get("category")
            editCategory.name = content
            editCategory.put()
        
        old_categorys = Category(name="",user=user)
        old_categorys = db.GqlQuery("SELECT * FROM Category WHERE user = :1", user)
        add_category = Category(name="",user=user)
        add_category.name = self.request.get('categoryToAdd')
        if( add_category.name ):
            add_category.put()
        
        template_values = {
            'category': add_category,
            'old_categorys': old_categorys,
            'user': user,
        }
        path = os.path.join(os.path.dirname(__file__),'html/addCategory.html')
        self.response.out.write(template.render(path,template_values))


class ChooseCategoryToResult(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        categorys = Category(name="",
                             user=users.get_current_user())
        categorys = db.GqlQuery("SELECT * FROM Category")
        template_values = {
            'categorys': categorys,
            'user': user,
        }
        path = os.path.join(os.path.dirname(__file__),'html/chooseCategoryToResult.html')
        self.response.out.write(template.render(path,template_values))


class ChooseCategoryToVote(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        categorys = Category(name="",
                             user = users.get_current_user())
        categorys = db.GqlQuery("SELECT * FROM Category")
        template_values = {
            'categorys': categorys,
            'user': user,
        }
        path = os.path.join(os.path.dirname(__file__),'html/chooseCategoryToVote.html')
        self.response.out.write(template.render(path,template_values))

class AddItem(webapp2.RequestHandler):
    def post(self):
        params = self.request.params
        if not params.has_key('category_key'):
            self.redirect('/')
        else:
            user = users.get_current_user()
            category_key= self.request.get("category_key")
            category = db.get(category_key)
            item = Item()
            item.name = self.request.get("itemToAdd")
            item.category = category
            item.put()
            template_values = {
                'user': user,
                'category':category,
                'old_items':category.items,
                'item':item,
            }
            path = os.path.join(os.path.dirname(__file__),'html/addItem.html')
            self.response.out.write(template.render(path,template_values))

class EditItem(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        category_key= self.request.get("category_key")
        category = db.get(category_key)
        item = Item()
        item.name = self.request.get("itemToAdd")
        item.category = category
        item.put()
        
        editedItem_key = self.request.get("editedItem")
        params = self.request.params
        editItem = db.get(editedItem_key)
        if params['submit'] == 'Delete':        
            editItem.delete()
        elif params['submit'] == 'Edit':
            content = self.request.get("item")
            editItem.name = content
            editItem.put()

        template_values = {
            'user': user,
            'category':category,
            'old_items':category.items,
            'item':item,
        }
        path = os.path.join(os.path.dirname(__file__),'html/addItem.html')
        self.response.out.write(template.render(path,template_values))


class ChooseCategoryToAddItems(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        categorys = Category(name="",user = user)
        categorys = db.GqlQuery("SELECT * FROM Category WHERE user = :1", user)
        template_values = {
            'categorys': categorys,
            'user': user,
        }
        path = os.path.join(os.path.dirname(__file__),'html/chooseCategoryToAddItem.html')
        self.response.out.write(template.render(path,template_values))

class ExportXML(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        objects = Category(name="",user=user)
        objects = db.GqlQuery("SELECT * FROM Category")
        xml = CategoryObjectsToXML(objects)
        return HttpResponse(xml)

def CategoryObjectsToXML(obj):
    xml = ""
    if obj:
        for i in obj:
            name = i.name
            tmp = "<Category><name>"+name+"</name>"
            for j in i.items:
                tmp = tmp+"<item><name>"+j.name+"</name></item>"
            xml = xml+tmp+"</Category>"
    
    return xml

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/chooseCategoryToVote',ChooseCategoryToVote),
                               ('/chooseCategoryToResult',ChooseCategoryToResult),
                               ('/result',Result),
                               ('/vote',Vote),
                               ('/recordVote',RecordVote),
                               ('/addCategory',AddCategory),
                               ('/editCategory',EditCategory),
                               ('/chooseCategoryToAddItems',ChooseCategoryToAddItems),
                               ('/editItem',EditItem),
                               ('/addItem',AddItem),
                               ('/exportXML',ExportXML)],
                               debug=True)
