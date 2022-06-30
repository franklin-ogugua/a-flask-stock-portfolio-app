from . import watchlist_blueprint
from flask import render_template, request, flash, current_app, redirect, url_for, abort
from flask_login import login_required, current_user
from .forms import WatchStockForm
from project import database
from project.models import WatchStock


@watchlist_blueprint.route('/watchlist')
@login_required
def watchlist():
    watchstocks = WatchStock.query.order_by(WatchStock.id).filter_by(user_id=current_user.id).all()
    for watchstock in watchstocks:
        watchstock.retrieve_current_share_price()
        watchstock.retrieve_stock_analysis_data()
        database.session.add(watchstock)
    database.session.commit()

    return render_template('watchlist/watchlist.html', watchstocks=watchstocks)


@watchlist_blueprint.route('/watchlist/add_watch_stock', methods=['GET', 'POST'])
@login_required
def add_watch_stock():
    form = WatchStockForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            new_watch_stock = WatchStock(form.stock_symbol.data, current_user.id)
            database.session.add(new_watch_stock)
            database.session.commit()
            flash(f'Added new stock ({form.stock_symbol.data}) to the watchlist!', 'success')
            current_app.logger.info(f'Added new watch stock ({form.stock_symbol.data}) '
                                    'for user {current_user.id}: {current_user.email}')
            return redirect(url_for('watchlist.watchlist'))

    return render_template('watchlist/add_watch_stock.html', form=form)


@watchlist_blueprint.route('/watchlist/<id>/delete')
@login_required
def delete_watch_stock(id):
    watchstock = WatchStock.query.filter_by(id=id).first_or_404()

    if watchstock.user_id != current_user.id:
        abort(403)

    database.session.delete(watchstock)
    database.session.commit()
    flash(f'Stock ({watchstock.stock_symbol}) was deleted!', 'success')
    current_app.logger.info(f'Stock ({watchstock.stock_symbol}) was deleted for user: {current_user.id}!')
    return redirect(url_for('watchlist.watchlist'))


@watchlist_blueprint.route('/stock_analysis_guide')
def stock_analysis_guide():
    return render_template('watchlist/stock_analysis_guide.html')
