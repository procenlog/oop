import csv
import simplejson
from decimal import *
from sys import exit


class Bond(object):
    def __init__(self, bond_id, price_dirty, profit, duration):
        if price_dirty == 'null':
            price_dirty = 0
        if profit == 'null':
            profit = 0
        if duration == 'null':
            duration = 0

        self.bond_id = int(bond_id)
        self.price_dirty = Decimal(price_dirty)
        self.profit = Decimal(profit)
        self.duration = Decimal(duration)


class BondManager(object):
    def __init__(self, filename):
        self.bond_list = []
        self.populate_bondmanager(filename)

    def populate_bondmanager(self, filename):
        with open(filename, 'rb') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                new_bond = Bond(row['bond_id'],
                                row['price_dirty'],
                                row['yield'],
                                row['duration'],
                                )
                self.bond_list.append(new_bond)

    def get_bond(self, search_id):
        for bond in self.bond_list:
            if bond.bond_id == search_id:
                return bond
        raise NameError("Bond with id {0} was not found".format(search_id))


class Asset(object):
    def __init__(self, bondit_id, units, portfolio):
        self.bondit_id = int(bondit_id)
        self.units = int(units)
        self.portfolio = portfolio

    @property
    def weight(self):
        bond = self.portfolio.bond_manager.get_bond(search_id=self.bondit_id)
        return (bond.price_dirty * self.units / portfolio.holding_value)


class Portfolio(object):
    def __init__(self, filename, bond_manager):
        self.assets = []
        self.bond_manager = bond_manager
        self.assets = self.populate_portfolio(filename)
        self.holding_value = self.get_holding_value()

    def populate_portfolio(self, filename):
        assets = []
        with open(filename) as json_file:
            data = simplejson.load(json_file)
            for asset in data['assets']:
                new_asset = Asset(asset['bondit_id'], asset['units'], self)
                assets.append(new_asset)
        return assets

    def get_holding_value(self):
        holding_value = 0
        for asset in self.assets:
            bond = self.bond_manager.get_bond(asset.bondit_id)
            holding_value += asset.units * bond.price_dirty
        return holding_value

    def get_portfolio_info(self):
        duration = 0
        total_return = 0

        for asset in self.assets:
            bond = self.bond_manager.get_bond(asset.bondit_id)
            duration += asset.weight * bond.duration
            total_return += asset.weight * bond.profit

        return {"holding_value": self.holding_value,
                "duration": duration,
                "total_return": total_return,
                }


if __name__ == "__main__":
    getcontext().prec = 4
    bond_manager = BondManager('bonds_trading_data.csv')
    portfolio = Portfolio('input.json', bond_manager)

    portfolio_info = portfolio.get_portfolio_info()
    exit(simplejson.dumps(portfolio_info))