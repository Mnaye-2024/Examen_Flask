from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, DateField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .models import User

class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

class RegistrationForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6, message='Le mot de passe doit faire au moins 6 caractères.')])
    confirm_password = PasswordField('Confirmer le mot de passe',
                                   validators=[DataRequired(), EqualTo('password', message='Les mots de passe doivent correspondre.')])
    submit = SubmitField('S\'inscrire')

    def validate_username(self, username):
        """Vérifie si le nom d'utilisateur existe déjà."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ce nom d\'utilisateur est déjà pris. Veuillez en choisir un autre.')

class TransactionForm(FlaskForm):
    amount = FloatField('Montant', validators=[DataRequired(message='Le montant est requis.')])
    date = DateField('Date', validators=[DataRequired(message='La date est requise.')], format='%Y-%m-%d')
    description = StringField('Description (Optionnel)')
    type = SelectField('Type', choices=[('expense', 'Dépense'), ('income', 'Revenu')],
                       validators=[DataRequired(message='Le type est requis.')])
    category = SelectField('Catégorie', coerce=int, validators=[DataRequired(message='La catégorie est requise.')])
    submit = SubmitField('Enregistrer')

class CategoryForm(FlaskForm):
    name = StringField('Nom de la catégorie', validators=[DataRequired(message='Le nom de la catégorie est requis.'), Length(max=50)])
    submit = SubmitField('Ajouter')