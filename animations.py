from flask import Blueprint, request, session, jsonify, redirect, render_template, url_for
from helpers import load_json, save_json
import time
import os

animations_bp = Blueprint('animations', __name__)

ANIMATIONS_FILE = 'animations.json'

@animations_bp.route('/create')
def create():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    return render_template('create.html')


@animations_bp.route('/save_animation', methods=['POST'])
def save_animation():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['user']
    animation_data = request.get_json()
    if not animation_data:
        return jsonify({'error': 'No animation data provided'}), 400

    animations = load_json(ANIMATIONS_FILE)
    user_animations = animations.get(username, [])

    animation_entry = {
        'id': int(time.time() * 1000),
        'data': animation_data
    }

    user_animations.append(animation_entry)
    animations[username] = user_animations
    save_json(ANIMATIONS_FILE, animations)

    return jsonify({
        'message': 'Animation saved successfully',
        'animation_id': animation_entry['id']
    }), 200


@animations_bp.route('/delete_animation', methods=['POST'])
def delete_animation():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    animation_id = int(request.form.get('id'))

    animations = load_json(ANIMATIONS_FILE)
    if user in animations:
        animations[user] = [a for a in animations[user] if a['id'] != animation_id]
        save_json(ANIMATIONS_FILE, animations)

    return redirect(url_for('animations.my_animations'))


@animations_bp.route('/my_animations')
def my_animations():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    animations = []
    all_animations = load_json(ANIMATIONS_FILE)
    animations = all_animations.get(user, [])

    return render_template('my_animations.html', user=user, animations=animations)
