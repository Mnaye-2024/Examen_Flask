# budget_app/app/routes.py
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, abort
)
from flask_login import login_user, logout_user, login_required, current_user
from . import db # Importe db depuis __init__.py
from .models import User, Transaction, Category
from .forms import TransactionForm, CategoryForm, LoginForm, RegistrationForm
from datetime import datetime, timedelta
from .utils import generate_pdf_report, generate_excel_report
from collections import defaultdict
import calendar

# Création d'un Blueprint pour organiser les routes
main_bp = Blueprint('main', __name__)

# --- Routes d'Authentification ---

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Si déjà connecté, redirige vers l'accueil
    form = RegistrationForm()
    if form.validate_on_submit():
        # Crée un nouvel utilisateur
        user = User(username=form.username.data)
        user.set_password(form.password.data) # Hashage du mot de passe
        db.session.add(user)
        db.session.commit()
        flash('Votre compte a été créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Inscription', form=form)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # Vérifie si l'utilisateur existe et si le mot de passe est correct
        if user and user.check_password(form.password.data):
            login_user(user) # Connecte l'utilisateur avec Flask-Login
            flash('Connexion réussie!', 'success')
            # Redirige vers la page demandée avant la connexion, ou vers l'index
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Échec de la connexion. Vérifiez le nom d\'utilisateur et le mot de passe.', 'danger')
    return render_template('login.html', title='Connexion', form=form)

@main_bp.route('/logout')
@login_required # Nécessite d'être connecté pour se déconnecter
def logout():
    logout_user() # Déconnecte l'utilisateur
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('main.login'))

# --- Routes Principales de l'Application ---

@main_bp.route('/')
@main_bp.route('/index')
@login_required # Protège cette route
def index():
    # Récupère les 10 dernières transactions de l'utilisateur connecté
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
                                   .order_by(Transaction.date.desc())\
                                   .limit(10).all()
    return render_template('index.html', title='Accueil', transactions=transactions)

@main_bp.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()

    form.category.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).order_by('name').all()]

    if not form.category.choices:
         flash('Veuillez d\'abord ajouter au moins une catégorie avant d\'enregistrer une transaction.', 'warning')
         # return redirect(url_for('main.categories'))

    if form.validate_on_submit():
        category = Category.query.filter_by(id=form.category.data, user_id=current_user.id).first()
        if not category:
            flash('Catégorie invalide sélectionnée.', 'danger')
            return render_template('add_transaction.html', title='Ajouter Transaction', form=form)

        transaction = Transaction(
            amount=form.amount.data,
            date=form.date.data,
            description=form.description.data,
            type=form.type.data,
            user_id=current_user.id,
            category_id=form.category.data
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction enregistrée avec succès!', 'success')
        return redirect(url_for('main.index'))
    elif request.method == 'POST':
        flash('Erreur dans le formulaire. Veuillez vérifier les champs.', 'danger')

    return render_template('add_transaction.html', title='Ajouter Transaction', form=form)

@main_bp.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        existing_category = Category.query.filter_by(user_id=current_user.id, name=form.name.data).first()
        if existing_category:
            flash('Une catégorie avec ce nom existe déjà.', 'warning')
        else:
            category = Category(name=form.name.data, user_id=current_user.id)
            db.session.add(category)
            db.session.commit()
            flash('Catégorie ajoutée avec succès!', 'success')
        return redirect(url_for('main.categories'))

    user_categories = Category.query.filter_by(user_id=current_user.id).order_by('name').all()
    return render_template('categories.html', title='Gérer les Catégories', form=form, categories=user_categories)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    total_incomes = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_incomes - total_expenses

    expenses_by_category = defaultdict(float)
    for t in transactions:
        if t.type == 'expense':
            if t.category:
                expenses_by_category[t.category.name] += t.amount
            else: 
                 expenses_by_category['Catégorie Supprimée'] += t.amount


    category_labels = list(expenses_by_category.keys())
    category_values = list(expenses_by_category.values())

    return render_template('dashboard.html',
                         title='Tableau de Bord',
                         total_incomes=total_incomes,
                         total_expenses=total_expenses,
                         balance=balance,
                         category_labels=category_labels,
                         category_values=category_values)


@main_bp.route('/get_chart_data')
@login_required
def get_chart_data():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.asc()).all()

    monthly_data = defaultdict(lambda: {'income': 0.0, 'expense': 0.0})

    if transactions:
        first_date = min(t.date for t in transactions)
        last_date = max(t.date for t in transactions)

        current_month = first_date.replace(day=1)

        while current_month <= last_date:
            month_str = current_month.strftime('%Y-%m')
            monthly_data[month_str]
            next_month = current_month.replace(day=28) + timedelta(days=4)
            current_month = next_month.replace(day=1)

        for t in transactions:
            month_str = t.date.strftime('%Y-%m')
            if t.type == 'income':
                monthly_data[month_str]['income'] += t.amount
            elif t.type == 'expense':
                monthly_data[month_str]['expense'] += t.amount

    sorted_months = sorted(monthly_data.keys())


    month_names_fr = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    chart_labels = []
    for month_str in sorted_months:
        year, month_num = map(int, month_str.split('-'))
        chart_labels.append(f"{month_names_fr[month_num-1]} {year}")

    income_values = [monthly_data[month]['income'] for month in sorted_months]
    expense_values = [monthly_data[month]['expense'] for month in sorted_months]

    data_for_chart = {
        'monthly': {
            'labels': chart_labels,
            'incomes': income_values,
            'expenses': expense_values
        }

    }

    return jsonify(data_for_chart)



@main_bp.route('/export', methods=['GET', 'POST'])
@login_required
def export():
    if request.method == 'POST':
        export_format = request.form.get('format')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        start_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Format de date de début invalide. Utilisez AAAA-MM-JJ.', 'danger')
                return render_template('export.html', title='Exporter')

        end_date = None
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1, seconds=-1)
            except ValueError:
                flash('Format de date de fin invalide. Utilisez AAAA-MM-JJ.', 'danger')
                return render_template('export.html', title='Exporter')

        query = Transaction.query.filter_by(user_id=current_user.id)

        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)

        transactions = query.order_by(Transaction.date.asc()).all()

        if not transactions:
            flash('Aucune transaction trouvée pour la période sélectionnée.', 'info')
            return render_template('export.html', title='Exporter')

        if export_format == 'pdf':
            try:
                pdf_file = generate_pdf_report(transactions, start_date, end_date)
                return send_file(pdf_file,
                                 as_attachment=True,
                                 download_name='rapport_budget.pdf',
                                 mimetype='application/pdf')
            except Exception as e:
                flash(f"Erreur lors de la génération du PDF: {e}", 'danger')
                print(f"PDF Generation Error: {e}")
                return redirect(url_for('main.export'))

        elif export_format == 'excel':
            try:
                excel_file = generate_excel_report(transactions, start_date, end_date)
                return send_file(excel_file,
                                 as_attachment=True,
                                 download_name='rapport_budget.xlsx',
                                 mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            except Exception as e:
                flash(f"Erreur lors de la génération du fichier Excel: {e}", 'danger')
                print(f"Excel Generation Error: {e}")
                return redirect(url_for('main.export'))

        else:
            flash('Format d\'export non valide.', 'danger')
            return redirect(url_for('main.export'))

    return render_template('export.html', title='Exporter')

@main_bp.route('/delete_category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        abort(403)

    if category.transactions:
        flash('Impossible de supprimer cette catégorie car des transactions y sont associées.', 'warning')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Catégorie supprimée avec succès.', 'success')

    return redirect(url_for('main.categories'))

@main_bp.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        abort(403)

    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction supprimée avec succès.', 'success')
    return redirect(request.referrer or url_for('main.index'))