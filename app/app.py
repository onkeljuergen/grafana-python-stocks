from flask import render_template, request, flash, redirect, url_for
from flask_apscheduler import APScheduler

from config import db, app
from models import Stock, StockOwning


@app.route('/stocks', methods=['GET'])
def show_all():
    fetched_stocks = Stock.query.all()
    db.session.close()

    return render_template('show_all.html', stocks=fetched_stocks)


@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form['name'] \
                or not request.form['acronym'] \
                or not request.form['stock_currency'] \
                or not request.form['quantity'] \
                or not request.form['buy_price']:
            flash('Alle Felder müssen ausgefüllt sein', 'error')

        else:
            owning = StockOwning(
                quantity=request.form['quantity'], 
                buy_price=request.form['buy_price'])
            
            stock = Stock.query.filter_by(acronym=request.form['acronym']).first()
            if not stock:
                stock = Stock(name=request.form['name'],
                          acronym=request.form['acronym'],
                          stock_currency=request.form['stock_currency'])
            stock.ownings.append(owning)

            db.session.add(stock)
            db.session.commit()
            db.session.close()

            flash('Wertpapier erfolgreich gespeichert')
            return redirect(url_for('show_all'))

    return render_template('add_new.html')


@app.route('/delete/<int:owning_id>', methods=['GET'])
def delete(owning_id):
    StockOwning.query.filter(StockOwning.id == owning_id).delete()

    for stock in Stock.query.all():
        if not stock.ownings:
            Stock.query.filter(Stock.id == stock.id).delete()

    db.session.commit()

    fetched_stocks = Stock.query.all()

    db.session.close()

    return render_template('show_all.html', stocks=fetched_stocks)


if __name__ == "__main__":
    db.create_all()

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.run(host="0.0.0.0", debug=True)
