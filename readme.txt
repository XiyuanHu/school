Readme:

My project is written in Python and deployed with App Engine. You can try my project by visting :http://xiyuanhu66.appspot.com

On the home page, I have 5 forms to handle five actions, including: view your category, view your items, vote, view results and export to XML. 

In "view your category" part, you can see all the categories you have added,(after login),edit and delete the categories.

In "view your items" part, you can see all the items belong to the chosen category. And you can edit and delete the item by click the button on the right of the item.

In "vote" part, first you need to choose a category. You can vote on all the categories stored in the project data store. For each vote, you can choose to 'Vote' or 'Skip'. If you 'Vote' and choose one of the two items, you will be showed  a new vote with two other items. If you 'Vote' without choose one of the two items, you will be showed the home page and start to choose again. If you 'Skip', you will be showed a next new vote.

In "view results" part, you need to choose a category first, as well. And you can see all the items belongs to this category with how many votes they win and lose.

In "export to XML" part, you will be showed the xml file with all the categories and items. 