from flask import Flask, render_template, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import csv
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///garage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

TOTAL_SPOTS = 50
PRICE_PER_HOUR = 10
SUBSCRIPTION_PRICES = {
    'daily': 50,
    'monthly': 500
}

CAR_TYPES = ['Private Car', 'Pickup Truck', 'Truck', 'Motorcycle', 'Bus', 'Microbus', 'Van', 'Tuk Tuk']


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(100))
    car_number = db.Column(db.String(50))
    car_type = db.Column(db.String(50))
    subscription = db.Column(db.String(20), default='hourly')
    entry_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    exit_time = db.Column(db.DateTime, nullable=True)
    total_price = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='Parked')


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('car_type', '')
    sub_filter = request.args.get('subscription', '')

    query = Car.query
    if search:
        query = query.filter(
            db.or_(
                Car.car_number.ilike(f'%{search}%'),
                Car.owner_name.ilike(f'%{search}%')
            )
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    if type_filter:
        query = query.filter_by(car_type=type_filter)
    if sub_filter:
        query = query.filter_by(subscription=sub_filter)

    cars = query.order_by(Car.id.desc()).all()
    parked_cars = Car.query.filter_by(status='Parked').count()
    available_spots = TOTAL_SPOTS - parked_cars
    total_revenue = db.session.query(db.func.sum(Car.total_price)).scalar() or 0

    today = datetime.now(timezone.utc).date()
    today_revenue = db.session.query(db.func.sum(Car.total_price)).filter(
        db.func.date(Car.exit_time) == today
    ).scalar() or 0

    return render_template(
        'index.html',
        cars=cars,
        available_spots=available_spots,
        total_revenue=round(total_revenue, 2),
        today_revenue=round(today_revenue, 2),
        parked_cars=parked_cars,
        now=datetime.now(timezone.utc),
        garage_full=parked_cars >= TOTAL_SPOTS,
        search=search,
        status_filter=status_filter,
        type_filter=type_filter,
        sub_filter=sub_filter,
        car_types=CAR_TYPES,
        total_cars=Car.query.count()
    )


@app.route('/add', methods=['GET', 'POST'])
def add_car():
    garage_full = Car.query.filter_by(status='Parked').count() >= TOTAL_SPOTS
    if request.method == 'POST':
        if garage_full:
            return redirect('/')
        subscription = request.form['subscription']
        car = Car(
            owner_name=request.form['owner_name'],
            car_number=request.form['car_number'],
            car_type=request.form['car_type'],
            subscription=subscription,
            total_price=SUBSCRIPTION_PRICES.get(subscription, 0) if subscription != 'hourly' else 0
        )  # type: ignore
        db.session.add(car)
        db.session.commit()
        return redirect('/')
    return render_template('add_car.html', garage_full=garage_full, car_types=CAR_TYPES,
                           subscription_prices=SUBSCRIPTION_PRICES)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_car(id):
    car = db.get_or_404(Car, id)
    if request.method == 'POST':
        car.owner_name = request.form['owner_name']
        car.car_number = request.form['car_number']
        car.car_type = request.form['car_type']
        car.subscription = request.form['subscription']
        db.session.commit()
        return redirect('/')
    return render_template('edit_car.html', car=car, car_types=CAR_TYPES,
                           subscription_prices=SUBSCRIPTION_PRICES)


@app.route('/checkout/<int:id>', methods=['POST'])
def checkout(id):
    car = db.get_or_404(Car, id)
    if car.status == 'Parked':
        car.exit_time = datetime.now(timezone.utc)
        if car.subscription == 'hourly':
            duration = car.exit_time - car.entry_time.replace(tzinfo=timezone.utc)
            hours = duration.total_seconds() / 3600
            car.total_price = PRICE_PER_HOUR if hours < 1 else round(hours * PRICE_PER_HOUR, 2)
        car.status = 'Exited'
        db.session.commit()
    return redirect('/')


@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    car = db.get_or_404(Car, id)
    db.session.delete(car)
    db.session.commit()
    return redirect('/')


@app.route('/export/csv')
def export_csv():
    cars = Car.query.order_by(Car.id.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Owner', 'Car Number', 'Type', 'Subscription', 'Entry', 'Exit', 'Price (EGP)', 'Status'])
    for car in cars:
        writer.writerow([
            car.id, car.owner_name, car.car_number, car.car_type, car.subscription,
            car.entry_time.strftime('%Y-%m-%d %H:%M') if car.entry_time else '',
            car.exit_time.strftime('%Y-%m-%d %H:%M') if car.exit_time else '',
            car.total_price, car.status
        ])
    output.seek(0)
    return Response(output, mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=garage_report.csv'})


@app.route('/report')
def report():
    today = datetime.now(timezone.utc).date()
    today_cars = Car.query.filter(db.func.date(Car.entry_time) == today).count()
    today_revenue = db.session.query(db.func.sum(Car.total_price)).filter(
        db.func.date(Car.exit_time) == today).scalar() or 0
    total_cars = Car.query.count()
    total_revenue = db.session.query(db.func.sum(Car.total_price)).scalar() or 0
    by_type = db.session.query(Car.car_type, db.func.count(Car.id)).group_by(Car.car_type).all()
    by_sub = db.session.query(Car.subscription, db.func.count(Car.id)).group_by(Car.subscription).all()
    return render_template('report.html',
                           today_cars=today_cars, today_revenue=round(today_revenue, 2),
                           total_cars=total_cars, total_revenue=round(total_revenue, 2),
                           by_type=by_type, by_sub=by_sub,
                           now=datetime.now(timezone.utc))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
