from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from backend import db
from backend.models.user import User
from backend.models.food_profile import FoodProfile
import json

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'error')
            return redirect(url_for('auth.register'))

        # create user
        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            city=request.form.get('city', '')
        )
        db.session.add(new_user)
        db.session.flush()

        # create food profile from onboarding quiz
        food_profile = FoodProfile(
            user_id=new_user.id,
            spice_tolerance=int(request.form.get('spice_tolerance', 5)),
            diet_type=request.form.get('diet_type', 'non-veg'),
            budget_min=int(request.form.get('budget_min', 200)),
            budget_max=int(request.form.get('budget_max', 800)),
        )

        # set vibes and cuisines from onboarding
        vibes = request.form.getlist('vibes')
        cuisines = request.form.getlist('cuisines')
        food_profile.set_vibes(vibes)
        food_profile.set_cuisines(cuisines)

        # default food DNA
        food_profile.set_food_dna({
            'Indian': 40,
            'Street Food': 20,
            'Italian': 15,
            'Asian': 15,
            'Desserts': 10
        })

        db.session.add(food_profile)
        db.session.commit()

        login_user(new_user)
        flash('Welcome to ForkFind!', 'success')
        return redirect(url_for('main.home'))

    return render_template('auth/register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user)
        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for('main.home'))

    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/me')
@login_required
def me():
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email,
        'city': current_user.city
    })