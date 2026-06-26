from django.contrib import admin

from pedagogy.models import Cours, RenduDevoir, TravailDirige, TravailPratique

admin.site.register(Cours)
admin.site.register(TravailDirige)
admin.site.register(TravailPratique)
admin.site.register(RenduDevoir)
