import os
from datetime import date, timedelta
from functools import wraps

from flask import Blueprint, render_template, abort, redirect, url_for
from flask_login import current_user
from sqlalchemy import func, desc

from models import db, User, UserSettings, FoodLog, WorkoutLog, WeightHistory, TdeeSnapshot, MealTemplate, WorkoutProgression

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=url_for('admin.dashboard')))
        allowed = [e.strip().lower() for e in os.environ.get('ADMIN_EMAIL', '').split(',') if e.strip()]
        if current_user.email.lower() not in allowed:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@admin_required
def dashboard():
    today    = date.today()
    week_ago = today - timedelta(days=7)

    # ── Platform counters ────────────────────────────────────
    total_users           = User.query.count()
    new_users_7d          = User.query.filter(User.created_at >= week_ago).count()
    active_users_7d       = User.query.filter(User.last_login  >= week_ago).count()
    total_food_entries    = FoodLog.query.count()
    total_workout_entries = WorkoutLog.query.count()
    total_tdee_calcs      = TdeeSnapshot.query.count()
    total_templates       = MealTemplate.query.count()
    total_progression     = WorkoutProgression.query.count()
    users_with_logs       = db.session.query(
                                func.count(func.distinct(FoodLog.user_id))).scalar() or 0

    # ── Daily signups last 7 days ────────────────────────────
    daily_signups = []
    for i in range(6, -1, -1):
        d     = today - timedelta(days=i)
        count = User.query.filter(func.date(User.created_at) == d).count()
        daily_signups.append({'day': d.strftime('%a')[:3], 'count': count, 'is_today': i == 0})

    # ── Daily active logs last 14 days ───────────────────────
    daily_logs = []
    for i in range(13, -1, -1):
        d     = today - timedelta(days=i)
        count = db.session.query(func.count(func.distinct(FoodLog.user_id)))\
                    .filter(FoodLog.log_date == d).scalar() or 0
        daily_logs.append({'day': d.strftime('%d %b'), 'count': count, 'is_today': i == 0})

    # ── Top 10 foods ─────────────────────────────────────────
    top_foods = db.session.query(
        FoodLog.food_name,
        func.count(FoodLog.id).label('cnt')
    ).group_by(FoodLog.food_name).order_by(desc('cnt')).limit(10).all()

    # ── Top 10 exercises (workout log) ───────────────────────
    top_exercises = db.session.query(
        WorkoutLog.exercise_name,
        func.count(WorkoutLog.id).label('cnt')
    ).group_by(WorkoutLog.exercise_name).order_by(desc('cnt')).limit(10).all()

    # ── Top lifts by progression (best 1RM per exercise) ─────
    top_lifts = db.session.query(
        WorkoutProgression.exercise_name,
        func.max(WorkoutProgression.one_rm_est).label('best_1rm'),
        func.max(WorkoutProgression.weight_kg).label('best_weight'),
        func.count(WorkoutProgression.id).label('sessions'),
        func.count(func.distinct(WorkoutProgression.user_id)).label('lifters'),
    ).group_by(WorkoutProgression.exercise_name)\
     .order_by(desc('sessions')).limit(10).all()

    # ── Most-saved meal templates ─────────────────────────────
    top_templates = db.session.query(
        MealTemplate.name,
        MealTemplate.total_cal,
        MealTemplate.total_protein,
        MealTemplate.meal_type,
        func.count(MealTemplate.id).label('cnt'),
    ).group_by(MealTemplate.name, MealTemplate.total_cal,
               MealTemplate.total_protein, MealTemplate.meal_type)\
     .order_by(desc('cnt')).limit(8).all()

    # ── User table with per-user stats ───────────────────────
    users = User.query.order_by(User.created_at.desc()).all()
    user_rows = []
    for u in users:
        days     = db.session.query(func.count(func.distinct(FoodLog.log_date)))\
                       .filter_by(user_id=u.id).scalar() or 0
        cal      = db.session.query(func.sum(FoodLog.calories))\
                       .filter_by(user_id=u.id).scalar() or 0
        last_log = db.session.query(func.max(FoodLog.log_date))\
                       .filter_by(user_id=u.id).scalar()
        tpl_cnt  = MealTemplate.query.filter_by(user_id=u.id).count()
        prg_cnt  = WorkoutProgression.query.filter_by(user_id=u.id).count()
        user_rows.append({
            'user': u, 'days': days,
            'total_cal': int(cal), 'last_log': last_log,
            'templates': tpl_cnt, 'progressions': prg_cnt,
        })

    return render_template('admin.html',
        total_users=total_users, new_users_7d=new_users_7d,
        active_users_7d=active_users_7d, users_with_logs=users_with_logs,
        total_food_entries=total_food_entries,
        total_workout_entries=total_workout_entries,
        total_tdee_calcs=total_tdee_calcs,
        total_templates=total_templates,
        total_progression=total_progression,
        daily_signups=daily_signups, daily_logs=daily_logs,
        top_foods=top_foods, top_exercises=top_exercises,
        top_lifts=top_lifts, top_templates=top_templates,
        user_rows=user_rows,
    )


@admin_bp.route('/user/<user_id>')
@admin_required
def user_detail(user_id):
    u  = User.query.get_or_404(user_id)
    s  = u.settings
    thirty_ago = date.today() - timedelta(days=30)

    food_logs    = (FoodLog.query.filter_by(user_id=u.id)
                    .filter(FoodLog.log_date >= thirty_ago)
                    .order_by(FoodLog.log_date.desc(), FoodLog.id.asc()).all())
    workout_logs = (WorkoutLog.query.filter_by(user_id=u.id)
                    .filter(WorkoutLog.log_date >= thirty_ago)
                    .order_by(WorkoutLog.log_date.desc()).all())
    tdee_snaps   = (TdeeSnapshot.query.filter_by(user_id=u.id)
                    .order_by(TdeeSnapshot.created_at.desc()).limit(5).all())
    weight_hist  = (WeightHistory.query.filter_by(user_id=u.id)
                    .order_by(WeightHistory.recorded_date.desc()).limit(30).all())

    # ── Meal templates ───────────────────────────────────────
    user_templates = (MealTemplate.query.filter_by(user_id=u.id)
                      .order_by(MealTemplate.created_at.desc()).all())

    # ── Workout progression — best lift per exercise ─────────
    prog_summary = db.session.query(
        WorkoutProgression.exercise_name,
        func.max(WorkoutProgression.one_rm_est).label('best_1rm'),
        func.max(WorkoutProgression.weight_kg).label('best_weight'),
        func.count(WorkoutProgression.id).label('sessions'),
        func.max(WorkoutProgression.log_date).label('last_date'),
    ).filter_by(user_id=u.id)\
     .group_by(WorkoutProgression.exercise_name)\
     .order_by(desc('best_1rm')).all()

    # ── Aggregate daily summary ───────────────────────────────
    daily = {}
    for f in food_logs:
        k = f.log_date.isoformat()
        daily.setdefault(k, {'food_cal': 0, 'workout_cal': 0, 'protein': 0})
        daily[k]['food_cal']  += f.calories
        daily[k]['protein']   += f.protein_g
    for w in workout_logs:
        k = w.log_date.isoformat()
        daily.setdefault(k, {'food_cal': 0, 'workout_cal': 0, 'protein': 0})
        daily[k]['workout_cal'] += w.calories_burned

    total_days        = len(daily)
    total_food_cal    = sum(v['food_cal']    for v in daily.values())
    total_workout_cal = sum(v['workout_cal'] for v in daily.values())

    return render_template('admin_user.html',
        u=u, s=s,
        daily=sorted(daily.items(), reverse=True),
        tdee_snaps=tdee_snaps,
        weight_hist=weight_hist,
        user_templates=user_templates,
        prog_summary=prog_summary,
        total_days=total_days,
        total_food_cal=int(total_food_cal),
        total_workout_cal=int(total_workout_cal),
        avg_daily_cal=int(total_food_cal / total_days) if total_days else 0,
    )
