import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id         = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    google_id  = db.Column(db.String(120), unique=True, nullable=False)
    email      = db.Column(db.String(255), unique=True, nullable=False)
    name       = db.Column(db.String(255))
    picture    = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    settings      = db.relationship('UserSettings',  back_populates='user', uselist=False, cascade='all, delete-orphan')
    food_logs     = db.relationship('FoodLog',        back_populates='user', cascade='all, delete-orphan')
    workout_logs  = db.relationship('WorkoutLog',     back_populates='user', cascade='all, delete-orphan')
    weight_history= db.relationship('WeightHistory',  back_populates='user', cascade='all, delete-orphan')
    tdee_snapshots= db.relationship('TdeeSnapshot',   back_populates='user', cascade='all, delete-orphan')


class UserSettings(db.Model):
    """One row per user — upserted on save."""
    __tablename__ = 'user_settings'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    calorie_goal = db.Column(db.Integer, default=2000)
    protein_g    = db.Column(db.Integer, default=150)
    carb_g       = db.Column(db.Integer, default=200)
    fat_g        = db.Column(db.Integer, default=65)
    weight_kg    = db.Column(db.Float,   default=70.0)
    diet_pref    = db.Column(db.String(10), default='all')  # 'veg', 'nonveg', 'all'
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='settings')


class FoodLog(db.Model):
    """One row per food item per meal per day."""
    __tablename__ = 'food_logs'

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    log_date  = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)   # breakfast/lunch/dinner/snacks
    food_name = db.Column(db.String(255), nullable=False)
    calories  = db.Column(db.Integer, default=0)
    protein_g = db.Column(db.Float, default=0)
    carb_g    = db.Column(db.Float, default=0)
    fat_g     = db.Column(db.Float, default=0)
    created_at= db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='food_logs')

    __table_args__ = (
        db.Index('idx_food_user_date', 'user_id', 'log_date'),
    )


class WorkoutLog(db.Model):
    """One row per exercise per day."""
    __tablename__ = 'workout_logs'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    log_date        = db.Column(db.Date, nullable=False)
    exercise_name   = db.Column(db.String(255), nullable=False)
    exercise_type   = db.Column(db.String(20))          # cardio / strength / custom
    description     = db.Column(db.String(255))
    calories_burned = db.Column(db.Integer, default=0)
    duration_minutes= db.Column(db.Float)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='workout_logs')

    __table_args__ = (
        db.Index('idx_workout_user_date', 'user_id', 'log_date'),
    )


class WeightHistory(db.Model):
    """Daily body-weight check-ins — one per user per date."""
    __tablename__ = 'weight_history'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    recorded_date = db.Column(db.Date, nullable=False)
    weight_kg     = db.Column(db.Float, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='weight_history')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'recorded_date', name='uq_weight_user_date'),
    )


class TdeeSnapshot(db.Model):
    """Saved every time the user runs the TDEE calculator — powers the analytics tab."""
    __tablename__ = 'tdee_snapshots'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    age            = db.Column(db.Integer)
    gender         = db.Column(db.String(10))
    height_cm      = db.Column(db.Float)
    weight_kg      = db.Column(db.Float)
    activity_level = db.Column(db.String(20))
    goal           = db.Column(db.String(30))
    bmr            = db.Column(db.Integer)
    tdee           = db.Column(db.Integer)
    goal_cal       = db.Column(db.Integer)
    protein_g      = db.Column(db.Integer)
    carb_g         = db.Column(db.Integer)
    fat_g          = db.Column(db.Integer)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='tdee_snapshots')


class MealTemplate(db.Model):
    """User-saved meal combos for one-click re-use."""
    __tablename__ = 'meal_templates'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name          = db.Column(db.String(100), nullable=False)
    meal_type     = db.Column(db.String(20), default='any')  # breakfast/lunch/dinner/snacks/any
    items         = db.Column(db.Text, nullable=False)        # JSON array of {name,cal,protein,carbs,fat}
    total_cal     = db.Column(db.Integer, default=0)
    total_protein = db.Column(db.Float,   default=0)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('meal_templates', cascade='all, delete-orphan', lazy=True))


class WorkoutProgression(db.Model):
    """Structured strength-session history — one row per logged strength set."""
    __tablename__ = 'workout_progression'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    log_date      = db.Column(db.Date, nullable=False)
    exercise_name = db.Column(db.String(255), nullable=False)
    sets          = db.Column(db.Integer, default=0)
    reps_per_set  = db.Column(db.Integer, default=0)
    weight_kg     = db.Column(db.Float, default=0)
    total_volume  = db.Column(db.Float, default=0)  # sets × reps × weight
    one_rm_est    = db.Column(db.Float, default=0)  # Epley: weight × (1 + reps/30)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('workout_progressions', cascade='all, delete-orphan', lazy=True))

    __table_args__ = (
        db.Index('idx_prog_user_exercise', 'user_id', 'exercise_name'),
    )
