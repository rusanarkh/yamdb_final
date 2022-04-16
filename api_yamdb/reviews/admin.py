from django.contrib import admin

from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre


class TitleGenreInline(admin.TabularInline):
    model = TitleGenre
    extra = 1


class GenreAdmin(admin.ModelAdmin):
    inlines = (TitleGenreInline,)


class TitleAdmin(admin.ModelAdmin):
    inlines = (TitleGenreInline,)


admin.site.register(Category)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(Title, TitleAdmin)
admin.site.register(Genre, GenreAdmin)
