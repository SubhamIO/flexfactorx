import json
from datetime import date, timedelta, datetime
from flask import Blueprint, request, jsonify
from flask_login import current_user
from sqlalchemy import func
from models import db, UserSettings, FoodLog, WorkoutLog, WeightHistory, TdeeSnapshot, MealTemplate, WorkoutProgression

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


# ── STREAK ────────────────────────────────────────────────────────────────────

@api_bp.route('/analytics/streak', methods=['GET'])
def get_streak():
    err = _auth_required()
    if err:
        return err
    today = date.today()

    # Current consecutive streak counting back from today
    current_streak = 0
    check = today
    while current_streak < 1000:
        if not FoodLog.query.filter_by(user_id=current_user.id, log_date=check).first():
            break
        current_streak += 1
        check = check - timedelta(days=1)

    # Total unique days tracked
    total_days = (db.session.query(func.count(func.distinct(FoodLog.log_date)))
                  .filter(FoodLog.user_id == current_user.id).scalar() or 0)

    # Longest streak — walk all logged dates in order
    all_dates = sorted(
        r[0] for r in db.session.query(func.distinct(FoodLog.log_date))
                                 .filter(FoodLog.user_id == current_user.id).all()
    )
    longest = cur = 0
    for i, d in enumerate(all_dates):
        cur = (cur + 1) if (i > 0 and (d - all_dates[i - 1]).days == 1) else 1
        longest = max(longest, cur)

    return jsonify({
        'current_streak':   current_streak,
        'longest_streak':   max(longest, current_streak),
        'total_days_tracked': total_days,
        'logged_today':     current_streak > 0,
    })


# ── ADAPTIVE TDEE ─────────────────────────────────────────────────────────────

@api_bp.route('/analytics/adaptive-tdee', methods=['GET'])
def adaptive_tdee():
    err = _auth_required()
    if err:
        return err
    today      = date.today()
    cutoff     = today - timedelta(days=28)

    # Average daily calories over last 28 days
    cal_rows = (db.session.query(FoodLog.log_date, func.sum(FoodLog.calories).label('cal'))
                .filter(FoodLog.user_id == current_user.id, FoodLog.log_date >= cutoff)
                .group_by(FoodLog.log_date).all())
    days_of_data = len(cal_rows)

    if days_of_data < 7:
        return jsonify({'status': 'insufficient_data', 'days_of_data': days_of_data, 'required': 7})

    avg_daily_cal = sum(r.cal for r in cal_rows) / days_of_data

    # Weight trend
    wh_entries = (WeightHistory.query
                  .filter(WeightHistory.user_id == current_user.id,
                          WeightHistory.recorded_date >= cutoff)
                  .order_by(WeightHistory.recorded_date.asc()).all())

    if len(wh_entries) < 2:
        return jsonify({
            'status':       'insufficient_weight_data',
            'days_of_data': days_of_data,
            'avg_calories': round(avg_daily_cal),
        })

    first_w      = wh_entries[0].weight_kg
    last_w       = wh_entries[-1].weight_kg
    span_days    = max((wh_entries[-1].recorded_date - wh_entries[0].recorded_date).days, 1)
    weekly_delta = (last_w - first_w) / span_days * 7   # kg/week

    # Adaptive TDEE:  avg_cal − (weekly_Δ × 7700 / 7)
    daily_cal_eq  = (weekly_delta * 7700) / 7
    adaptive_tdee_val = round(avg_daily_cal - daily_cal_eq)

    latest_snap = (TdeeSnapshot.query.filter_by(user_id=current_user.id)
                   .order_by(TdeeSnapshot.created_at.desc()).first())
    formula_tdee = latest_snap.tdee if latest_snap else None

    confidence = ('high' if days_of_data >= 21 and len(wh_entries) >= 4
                  else 'medium' if days_of_data >= 14 and len(wh_entries) >= 2
                  else 'low')

    gap = (adaptive_tdee_val - formula_tdee) if formula_tdee else 0
    if abs(gap) < 50:
        rec = 'Your formula TDEE closely matches your real metabolism. The calculator is accurate for you.'
    elif gap > 0:
        rec = (f'Your real metabolism burns {abs(gap)} cal/day MORE than the formula predicted. '
               f'You can eat up to {abs(gap)} cal more and still hit your goal.')
    else:
        rec = (f'Your real metabolism burns {abs(gap)} cal/day LESS than the formula predicted. '
               f'Tighten calories by {abs(gap)} cal to match your actual rate.')

    return jsonify({
        'status':                 'ok',
        'adaptive_tdee':          adaptive_tdee_val,
        'formula_tdee':           formula_tdee,
        'avg_calories':           round(avg_daily_cal),
        'weekly_weight_change_kg': round(weekly_delta, 3),
        'days_of_data':           days_of_data,
        'weight_entries':         len(wh_entries),
        'confidence':             confidence,
        'gap':                    gap,
        'recommendation':         rec,
        'first_weight':           first_w,
        'last_weight':            last_w,
    })


# ── WORKOUT PROGRESSION ───────────────────────────────────────────────────────

@api_bp.route('/analytics/progression', methods=['GET'])
def get_progression():
    err = _auth_required()
    if err:
        return err
    exercise = request.args.get('exercise', '').strip()
    limit    = min(int(request.args.get('limit', 20)), 50)

    if not exercise:
        # Return distinct exercise names the user has progression data for
        names = (db.session.query(func.distinct(WorkoutProgression.exercise_name))
                 .filter(WorkoutProgression.user_id == current_user.id).all())
        return jsonify({'exercises': [n[0] for n in names]})

    entries = (WorkoutProgression.query
               .filter_by(user_id=current_user.id, exercise_name=exercise)
               .order_by(WorkoutProgression.log_date.desc())
               .limit(limit).all())
    return jsonify([{
        'date':         e.log_date.isoformat(),
        'sets':         e.sets,
        'reps_per_set': e.reps_per_set,
        'weight_kg':    e.weight_kg,
        'total_volume': e.total_volume,
        'one_rm_est':   e.one_rm_est,
    } for e in entries])


@api_bp.route('/analytics/progression', methods=['POST'])
def save_progression():
    err = _auth_required()
    if err:
        return err
    data     = request.get_json() or {}
    exercise = data.get('exercise_name', '').strip()
    sets     = int(data.get('sets', 0))
    reps     = int(data.get('reps', 0))
    weight   = float(data.get('weight_kg', 0))
    if not exercise or not sets or not reps:
        return jsonify({'error': 'exercise_name, sets, reps required'}), 400

    volume  = sets * reps * weight
    one_rm  = round(weight * (1 + reps / 30), 1) if weight > 0 else 0

    entry = WorkoutProgression(
        user_id=current_user.id, log_date=date.today(),
        exercise_name=exercise, sets=sets, reps_per_set=reps,
        weight_kg=weight, total_volume=volume, one_rm_est=one_rm,
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'id': entry.id, 'one_rm_est': one_rm})


# ── COPY PREVIOUS DAY ─────────────────────────────────────────────────────────

@api_bp.route('/tracker/copy-day', methods=['POST'])
def copy_previous_day():
    err = _auth_required()
    if err:
        return err
    data      = request.get_json() or {}
    to_date   = _parse_date(data.get('to_date'))
    from_date = to_date - timedelta(days=1)

    prev = FoodLog.query.filter_by(user_id=current_user.id, log_date=from_date).all()
    if not prev:
        return jsonify({'ok': False, 'message': 'Nothing logged yesterday', 'copied': 0})

    today_names = {(e.meal_type, e.food_name)
                   for e in FoodLog.query.filter_by(user_id=current_user.id, log_date=to_date).all()}
    copied = 0
    for e in prev:
        if (e.meal_type, e.food_name) in today_names:
            continue
        db.session.add(FoodLog(
            user_id=current_user.id, log_date=to_date, meal_type=e.meal_type,
            food_name=e.food_name, calories=e.calories,
            protein_g=e.protein_g, carb_g=e.carb_g, fat_g=e.fat_g,
        ))
        copied += 1
    db.session.commit()

    # Return the full updated day so the frontend can refresh state
    all_today   = FoodLog.query.filter_by(user_id=current_user.id, log_date=to_date).all()
    food_log    = {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []}
    for e in all_today:
        food_log[e.meal_type].append({'id': e.id, 'name': e.food_name,
                                      'cal': e.calories, 'protein': e.protein_g,
                                      'carbs': e.carb_g, 'fat': e.fat_g})
    return jsonify({'ok': True, 'copied': copied, 'food_log': food_log})


# ── MEAL TEMPLATES ────────────────────────────────────────────────────────────

@api_bp.route('/tracker/templates', methods=['GET'])
def list_templates():
    err = _auth_required()
    if err:
        return err
    templates = (MealTemplate.query.filter_by(user_id=current_user.id)
                 .order_by(MealTemplate.created_at.desc()).all())
    return jsonify([{
        'id':            t.id,
        'name':          t.name,
        'meal_type':     t.meal_type,
        'items':         json.loads(t.items or '[]'),
        'total_cal':     t.total_cal,
        'total_protein': t.total_protein,
    } for t in templates])


@api_bp.route('/tracker/templates', methods=['POST'])
def create_template():
    err = _auth_required()
    if err:
        return err
    data  = request.get_json() or {}
    name  = data.get('name', '').strip()
    items = data.get('items', [])
    if not name or not items:
        return jsonify({'error': 'name and items required'}), 400

    t = MealTemplate(
        user_id      = current_user.id,
        name         = name,
        meal_type    = data.get('meal_type', 'any'),
        items        = json.dumps(items),
        total_cal    = int(sum(i.get('cal', 0) for i in items)),
        total_protein= float(sum(i.get('protein', 0) for i in items)),
    )
    db.session.add(t)
    db.session.commit()
    return jsonify({'id': t.id, 'ok': True})


@api_bp.route('/tracker/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    err = _auth_required()
    if err:
        return err
    t = MealTemplate.query.filter_by(id=template_id, user_id=current_user.id).first()
    if t:
        db.session.delete(t)
        db.session.commit()
    return jsonify({'ok': True})
