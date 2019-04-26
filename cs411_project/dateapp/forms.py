from django import forms

GENRE_CHOIES=((0,'Action' ), (1, 'Adventure'),(2,'Animation'),(3,'Comedy'),(4,'Crime'),(5,'Documentary'),(6,'Drama'),(7,'Family'),(8,'Fantasy'),(9,'History'))
class genreform(forms.Form):
    movie_genre=forms.ChoiceField(choices=GENRE_CHOIES)