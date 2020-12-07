import datetime
import yahoo_fin.stock_info as si
from influxdb import InfluxDBClient
from sqlalchemy.exc import InvalidRequestError
from config import EnvironConfig, db
from models import Stock

if EnvironConfig.influx_host:
    print('Connect to influxDB: {}'.format(EnvironConfig.influx_host))
    influxdbClient = InfluxDBClient(
        host=EnvironConfig.influx_host,
        udp_port=EnvironConfig.influx_port,
        use_udp=True,
        database=EnvironConfig.influx_db,
        ssl=False,
        verify_ssl=False)
else:
    print('No influxDB configured')


def update_influxdb_task():
    if EnvironConfig.influx_host:
        try:
            check_and_create_influx_db()
            measurements = retrieve_stocks()
            success = influxdbClient.write_points(measurements)
            print('{}: Data was send {}'.format(datetime.datetime.now(), success))
        except InvalidRequestError as db_exc:
            print('DB Error occured (rolling back): {}'.format(db_exc))
            db.session.rollback()
        except Exception as err:
            print('Error occured: {}'.format(err))
        finally:
            db.session.close()
            
def check_and_create_influx_db():
    db_exists = False
    databases = influxdbClient.get_list_database()
    for db in databases:
        if db['name'] == EnvironConfig.influx_db:
            db_exists = True
            break
    
    if not db_exists:
        influxdbClient.create_database(EnvironConfig.influx_db)
    
    influxdbClient.switch_database(EnvironConfig.influx_db)

def retrieve_stocks():
    stocks = Stock.query.all()

    measurements = []

    for stock in stocks:
        if stock.stock_currency == 'USD':
            euro_to_dollar = si.get_live_price('EURUSD=X')
        else:
            euro_to_dollar = 1

        last_price = 1/euro_to_dollar * si.get_live_price(stock.acronym)

        profit = calculate_profit(stock=stock, last_stock_value=last_price)
        percent = calculate_percent(stock=stock, last_stock_value=last_price)
        measurement = create_measurement(
            stock=stock, last=last_price, profit=profit, percent=percent)
        measurements.append(measurement)

    return measurements


def calculate_profit(stock, last_stock_value):
    value = 0.0

    for owning in stock.ownings:
        buy_sum = owning.quantity * owning.buy_price
        current_sum = owning.quantity * last_stock_value

        value = value + (current_sum - buy_sum)

    return value

def calculate_percent(stock, last_stock_value):
    buy_sum = 0.0
    current_sum = 0.0

    for owning in stock.ownings:
        buy_sum = buy_sum + owning.quantity * owning.buy_price
        current_sum = current_sum + owning.quantity * last_stock_value
    
    return (100 / buy_sum * current_sum - 100)


def create_measurement(stock, last, profit, percent):
    return {
        "measurement": "stocks",
        "tags": {
            "name": stock.name,
        },
        "fields": {
            "course": last,
            "quantity": sum(map(lambda o: o.quantity, stock.ownings)),
            "percent": percent,
            "profit": profit
        }
    }
