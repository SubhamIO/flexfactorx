from datetime import date, timedelta, datetime
from flask import Blueprint, request, jsonify
from flask_login import current_user
from sqlalchemy import func
from models import db, UserSettings, FoodLog, WorkoutLog, WeightHistory, TdeeSnapshot

api_bp = Blueprint('api', __name__, url_prefix='/api')


def _auth_required():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Login required', 'login_required': True}), 401
    return None


def _parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return date.today()


# ── SETTINGS ─────────────────────────────────────────────────────────────────

@api_bp.route('/tracker/settings', methods=['GET'])
def get_settings():
    err = _auth_required()
    if err:
        return err
    s = current_user.settings
    if not s:
        return jsonify({'cal': 2000, 'protein': 150, 'carbs': 200, 'fat': 65, 'bw': 70.0})
    return jsonify({
        'cal':     s.calorie_goal,
        'protein': s.protein_g,
        'carbs':   s.carb_g,
        'fat':     s.fat_g,
        'bw':      s.weight_kg,
    })


@api_bp.route('/tracker/settings', methods=['POST'])
def save_settings():
    err = _auth_required()
    if err:
        return err
    data = request.get_json() or {}
    s = current_user.settings
    if not s:
        s = UserSettings(user_id=current_user.id)
        db.session.add(s)
    s.calorie_goal = int(data.get('cal',     s.calorie_goal or 2000))
    s.protein_g    = int(data.get('protein', s.protein_g    or 150))
    s.carb_g       = int(data.get('carbs',   s.carb_g       or 200))
    s.fat_g        = int(data.get('fat',     s.fat_g        or 65))
    s.weight_kg    = float(data.get('bw',    s.weight_kg    or 70.0))
    db.session.commit()

    # Also record weight history when body weight changes
    today = date.today()
    wh = WeightHistory.query.filter_by(user_id=current_user.id, recorded_date=today).first()
    if not wh:
        db.session.add(WeightHistory(user_id=current_user.id, recorded_date=today, weight_kg=s.weight_kg))
        db.session.commit()

    return jsonify({'ok': True})


# ── DAY LOG (food + workout together) ────────────────────────────────────────

@api_bp.route('/tracker/day', methods=['GET'])
def get_day():
    err = _auth_required()
    if err:
        return err
    d = _parse_date(request.args.get('date'))

    food_entries    = FoodLog.query.filter_by(user_id=current_user.id, log_date=d).all()
    workout_entries = WorkoutLog.query.filter_by(user_id=current_user.id, log_date=d).all()

    food_log = {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []}
    for e in food_entries:
        food_log[e.meal_type].append({
            'id':      e.id,
            'name':    e.food_name,
            'cal':     e.calories,
            'protein': e.protein_g,
            'carbs':   e.carb_g,
            'fat':     e.fat_g,
        })

    workouts = [{
        'id':   w.id,
        'name': w.exercise_name,
        'desc': w.description or '',
        'cal':  w.calories_burned,
    } for w in workout_entries]

    return jsonify({'food_log': food_log, 'workouts': workouts})


# ── FOOD CRUD ─────────────────────────────────────────────────────────────────

@api_bp.route('/tracker/food', methods=['POST'])
def add_food():
    err = _auth_required()
    if err:
        return err
    data = request.get_json() or {}
    entry = FoodLog(
        user_id   = current_user.id,
        log_date  = _parse_date(data.get('date')),
        meal_type = data.get('meal_type', 'snacks'),
        food_name = data.get('name', ''),
        calories  = int(data.get('cal', 0)),
        protein_g = float(data.get('protein', 0)),
        carb_g    = float(data.get('carbs', 0)),
        fat_g     = float(data.get('fat', 0)),
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'id': entry.id})


@api_bp.route('/tracker/food/<int:entry_id>', methods=['DELETE'])
def delete_food(entry_id):
    err = _auth_required()
    if err:
        return err
    entry = FoodLog.query.filter_by(id=entry_id, user_id=current_user.id).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
    return jsonify({'ok': True})


# ── WORKOUT CRUD ──────────────────────────────────────────────────────────────

@api_bp.route('/tracker/workout', methods=['POST'])
def add_workout():
    err = _auth_required()
    if err:
        return err
    data = request.get_json() or {}
    entry = WorkoutLog(
        user_id         = current_user.id,
        log_date        = _parse_date(data.get('date')),
        exercise_name   = data.get('name', ''),
        exercise_type   = data.get('type', 'custom'),
        description     = data.get('desc', ''),
        calories_burned = int(data.get('cal', 0)),
        duration_minutes= data.get('duration'),
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'id': entry.id})


@api_bp.route('/tracker/workout/<int:entry_id>', methods=['DELETE'])
def delete_workout(entry_id):
    err = _auth_required()
    if err:
        return err
    entry = WorkoutLog.query.filter_by(id=entry_id, user_id=current_user.id).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
    return jsonify({'ok': True})


# ── 7-DAY WEEKLY SUMMARY ──────────────────────────────────────────────────────

@api_bp.route('/tracker/weekly', methods=['GET'])
def weekly():
    err = _auth_required()
    if err:
        return err
    today  = date.today()
    result = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        food_cal    = db.session.query(func.sum(FoodLog.calories)).filter_by(
                          user_id=current_user.id, log_date=d).scalar() or 0
        workout_cal = db.session.query(func.sum(WorkoutLog.calories_burned)).filter_by(
                          user_id=current_user.id, log_date=d).scalar() or 0
        result.append({
            'date':        d.isoformat(),
            'day':         d.strftime('%a')[:3].upper(),
            'food_cal':    int(food_cal),
            'workout_cal': int(workout_cal),
            'net':         int(food_cal) - int(workout_cal),
            'is_today':    i == 0,
        })
    return jsonify(result)


# ── TDEE SNAPSHOT ─────────────────────────────────────────────────────────────

@api_bp.route('/tracker/tdee', methods=['POST'])
def save_tdee():
    err = _auth_required()
    if err:
        return err
    data = request.get_json() or {}
    snap = TdeeSnapshot(
        user_id        = current_user.id,
        age            = data.get('age'),
        gender         = data.get('gender'),
        height_cm      = data.get('height_cm'),
        weight_kg      = data.get('weight_kg'),
        activity_level = data.get('activity_level'),
        goal           = data.get('goal'),
        bmr            = data.get('bmr'),
        tdee           = data.get('tdee'),
        goal_cal       = data.get('goal_cal'),
        protein_g      = data.get('protein_g'),
        carb_g         = data.get('carb_g'),
        fat_g          = data.get('fat_g'),
    )
    db.session.add(snap)

    # Auto-update user settings with fresh TDEE targets
    s = current_user.settings
    if not s:
        s = UserSettings(user_id=current_user.id)
        db.session.add(s)
    if data.get('goal_cal'):  s.calorie_goal = data['goal_cal']
    if data.get('protein_g'): s.protein_g    = data['protein_g']
    if data.get('carb_g'):    s.carb_g       = data['carb_g']
    if data.get('fat_g'):     s.fat_g        = data['fat_g']
    if data.get('weight_kg'): s.weight_kg    = data['weight_kg']

    db.session.commit()
    return jsonify({'ok': True})


# ── WEIGHT HISTORY ────────────────────────────────────────────────────────────

@api_bp.route('/tracker/weight', methods=['POST'])
def log_weight():
    err = _auth_required()
    if err:
        return err
    data = request.get_json() or {}
    weight_kg = data.get('weight_kg')
    if not weight_kg:
        return jsonify({'error': 'weight_kg required'}), 400

    today = date.today()
    wh = WeightHistory.query.filter_by(user_id=current_user.id, recorded_date=today).first()
    if wh:
        wh.weight_kg = weight_kg
    else:
        db.session.add(WeightHistory(user_id=current_user.id, recorded_date=today, weight_kg=weight_kg))
    db.session.commit()
    return jsonify({'ok': True})


@api_bp.route('/analytics/weight-history', methods=['GET'])
def weight_history():
    err = _auth_required()
    if err:
        return err
    entries = (WeightHistory.query
               .filter_by(user_id=current_user.id)
               .order_by(WeightHistory.recorded_date)
               .limit(90).all())
    return jsonify([{'date': e.recorded_date.isoformat(), 'weight_kg': e.weight_kg} for e in entries])


# ── ANALYTICS SUMMARY ─────────────────────────────────────────────────────────

@api_bp.route('/analytics/summary', methods=['GET'])
def analytics_summary():
    err = _auth_required()
    if err:
        return err
    today = date.today()

    # Consecutive-day logging streak
    streak     = 0
    check_date = today
    while streak < 366:
        count = FoodLog.query.filter_by(user_id=current_user.id, log_date=check_date).count()
        if not count:
            break
        streak    += 1
        check_date = check_date - timedelta(days=1)

    # 7-day average net calories
    week_ago   = today - timedelta(days=7)
    daily_rows = (db.session.query(FoodLog.log_date, func.sum(FoodLog.calories).label('food'),
                                   func.sum(WorkoutLog.calories_burned).label('workout'))
                  .outerjoin(WorkoutLog, (WorkoutLog.user_id == FoodLog.user_id) &
                              (WorkoutLog.log_date == FoodLog.log_date))
                  .filter(FoodLog.user_id == current_user.id, FoodLog.log_date >= week_ago)
                  .group_by(FoodLog.log_date).all())
    avg_net = int(sum((r.food or 0) - (r.workout or 0) for r in daily_rows) / len(daily_rows)) if daily_rows else 0

    # Latest body weight
    latest_wh = (WeightHistory.query
                 .filter_by(user_id=current_user.id)
                 .order_by(WeightHistory.recorded_date.desc()).first())

    # Total days with any food logged
    total_days = (db.session.query(func.count(func.distinct(FoodLog.log_date)))
                  .filter_by(user_id=current_user.id).scalar() or 0)

    # Goal adherence: days this week where net ≤ calorie goal
    s            = current_user.settings
    goal         = s.calorie_goal if s else 2000
    adherent     = sum(1 for r in daily_rows if ((r.food or 0) - (r.workout or 0)) <= goal)
    adherence_pct= round(adherent / len(daily_rows) * 100) if daily_rows else 0

    return jsonify({
        'streak':            streak,
        'avg_net_cal_7d':    avg_net,
        'latest_weight':     latest_wh.weight_kg if latest_wh else None,
        'total_days_tracked': total_days,
        'goal_adherence_pct': adherence_pct,
    })


# ── BULK MIGRATE (localStorage → DB on first login) ──────────────────────────

@api_bp.route('/tracker/migrate', methods=['POST'])
def migrate_local():
    """Accepts localStorage export and imports it — skips dates already in DB."""
    err = _auth_required()
    if err:
        return err
    data         = request.get_json() or {}
    settings_raw = data.get('settings')
    food_days    = data.get('food_days', {})      # {YYYY-MM-DD: {breakfast:[...], ...}}
    workout_days = data.get('workout_days', {})   # {YYYY-MM-DD: [{name,desc,cal},...]}

    if settings_raw:
        s = current_user.settings
        if not s:
            s = UserSettings(user_id=current_user.id)
            db.session.add(s)
        s.calorie_goal = int(settings_raw.get('cal',     2000))
        s.protein_g    = int(settings_raw.get('protein', 150))
        s.carb_g       = int(settings_raw.get('carbs',   200))
        s.fat_g        = int(settings_raw.get('fat',     65))
        s.weight_kg    = float(settings_raw.get('bw',    70.0))

    for date_str, log in food_days.items():
        d       = _parse_date(date_str)
        existing= FoodLog.query.filter_by(user_id=current_user.id, log_date=d).count()
        if existing:
            continue
        for meal_type, entries in (log or {}).items():
            for e in (entries or []):
                db.session.add(FoodLog(
                    user_id=current_user.id, log_date=d, meal_type=meal_type,
                    food_name=e.get('name', ''), calories=int(e.get('cal', 0)),
                    protein_g=float(e.get('protein', 0)), carb_g=float(e.get('carbs', 0)),
                    fat_g=float(e.get('fat', 0)),
                ))

    for date_str, wks in workout_days.items():
        d       = _parse_date(date_str)
        existing= WorkoutLog.query.filter_by(user_id=current_user.id, log_date=d).count()
        if existing:
            continue
        for w in (wks or []):
            db.session.add(WorkoutLog(
                user_id=current_user.id, log_date=d,
                exercise_name=w.get('name', ''), description=w.get('desc', ''),
                calories_burned=int(w.get('cal', 0)),
            ))

    db.session.commit()
    return jsonify({'ok': True, 'imported_food_days': len(food_days), 'imported_workout_days': len(workout_days)})
