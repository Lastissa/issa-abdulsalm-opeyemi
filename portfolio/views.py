from django.views import View
from django.shortcuts import render

class SitemapView(View):
    def get(self, request):
        item ={} # hOLD THE CONTENT THE SITEMAP IS SUPPOSED TO DISPLAY
        return render(request, "portfolio/sitemap.xml",{"item": item}, content_type="application/xml")
    
class Favico(View):
    def get(self, request):
        # Logic to generate and return the favicon response
        return render(request, "portfolio/favicon.ico", content_type="image/x-icon")
    
class HomeView(View):
    def get(self, request):
        return render(request, "portfolio/home.html")