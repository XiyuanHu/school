#!/usr/bin/env python
from __future__ import with_statement
from google.appengine.ext import blobstore
from google.appengine.api import files

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
            if count < 2:
                error_info = "You need at least two items to vote"
                firstItem = Item()
                secondItem = Item()
            else:
                firstIndex = random.randint(0,count-1)
                secondIndex = random.randint(0,count-1)
                while (firstIndex == secondIndex):
                    secondIndex = random.randint(0,count-1)
                firstItem = randomlist[firstIndex]
                secondItem = randomlist[secondIndex] 
                error_info = ""
    
            template_values = {
                'category': category,
                'user':user,
                'firstItem': firstItem,
                'secondItem': secondItem,
                'error_info':error_info,
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
            error_info=""
        else :
            error_info = "You can not add a category without name!"
        template_values = {
            'category': add_category,
            'old_categorys': old_categorys,
            'user': user,
            'error_info':error_info,
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
            if (item.name):
                item.put()
                error_info = ""
            else:
                error_info = "You can not add an item without name"

            template_values = {
                'user': user,
                'category':category,
                'old_items':category.items,
                'item':item,
                'error_info':error_info,
            }
            path = os.path.join(os.path.dirname(__file__),'html/addItem.html')
            self.response.out.write(template.render(path,template_values))

class EditItem(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        category_key= self.request.get("category_key")
        category = db.get(category_key)
               
        editedItem_key = self.request.get("editedItem")
        editItem = db.get(editedItem_key)
        params = self.request.params
        if params['submit'] == 'Delete':        
            editItem.delete()
        elif params['submit'] == 'Edit':
            content = self.request.get("item")
            editItem.name = content
            if (editItem.name):
                editItem.put()

        template_values = {
            'user': user,
            'category':category,
            'old_items':category.items,
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
    def get(self):
        user = users.get_current_user()
        objects = Category(name="",user=user)
        objects = db.GqlQuery("SELECT * FROM Category")
        template_values = {
            'categories': objects,
            'user': user,
        }
        path = os.path.join(os.path.dirname(__file__),'html/chooseCategoryToXML.html')
        self.response.out.write(template.render(path,template_values))

class ChooseCategoryToXML(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        category_key= self.request.get("category_key")
        category = db.get(category_key)
       
        template_values = {
            'category': category,
            'user': user,
        }
        path = os.path.join(os.path.dirname(__file__),'html/exportXML.html')
        self.response.out.write(template.render(path,template_values))

class CategoryXML(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        category_key= self.request.get("category")
        category = db.get(category_key)
        items = category.items
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.write('<?xml version="1.0" encoding="UTF-8"?>')
        self.response.write('<CATEGORY>')
        self.response.write('<NAME>' + category.name + '</NAME>')
        for item in items :
            self.response.write('<ITEM>')
            self.response.write('<NAME>' + item.name + '</NAME>')
            self.response.write('</ITEM>')
        self.response.write('</CATEGORY>')

class ImportXML(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_values = {
            'user': user,
        }
        path = os.path.join(os.path.dirname(__file__),'html/importXML.html')
        self.response.out.write(template.render(path,template_values))

class UploadXML(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        xmlfile=self.request.get("filename")
        xmlfile = xmlfile.split('\n')
        add_category = Category(name="",user = user)
        add_itemsName = []
        for i in xmlfile:
              if "<NAME>" in i :
                i = i[i.find('<NAME>')+6:i.find('</NAME>')]
                add_itemsName.append(i)
    
        add_category.name = add_itemsName[0]
        add_itemsName.remove(add_category.name)
        categories = db.GqlQuery("SELECT * FROM Category WHERE user = :1",user)
        cIsAdded = -1
        oldCategory = Category(name="",user=user)
        for category in categories:
            if category.name == add_category.name :
                oldCategory = category
                cIsAdded = 1
            
        if cIsAdded == -1 :
            add_category.put()
            for item in add_itemsName:
                newItem = Item(name=item,user=user,category=add_category)
                newItem.put()
        elif cIsAdded == 1:
            c = db.GqlQuery("SELECT * FROM Category WHERE name = :1",add_category.name)
            for i in oldCategory.items:
                if not i.name in add_itemsName:
                    i.delete()
            alreadHave = []
            for i in oldCategory.items:
                alreadHave.append(i.name)
            names = []
            for i in add_itemsName:
                names.append(i)
            for i in names:
                if i in alreadHave:
                    add_itemsName.remove(i)
            for item in add_itemsName:
                nItem = Item(name=item,user=user,category=c[0])
                nItem.put()

        old_categorys = db.GqlQuery("SELECT * FROM Category WHERE user = :1",user)
        template_values = {
            'old_categorys': old_categorys,
            'user': user,
        }
        path = os.path.join(os.path.dirname(__file__),'html/addCategory.html')
        self.response.out.write(template.render(path,template_values))




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
                               ('/categoryXML',CategoryXML),
                               ('/chooseCategoryToXML',ChooseCategoryToXML),
                               ('/exportXML',ExportXML),
                               ('/importXML',ImportXML),
                               ('/uploadXML',UploadXML)],
                               debug=True)
