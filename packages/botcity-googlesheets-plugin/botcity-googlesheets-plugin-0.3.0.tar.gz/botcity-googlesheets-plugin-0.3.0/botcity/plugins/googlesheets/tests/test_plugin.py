import os
from botcity.plugins.googlesheets import BotGoogleSheetsPlugin

cur_path = os.path.abspath(os.path.dirname(__file__))

reference = [
    ['Name', 'Mana', 'Price', 'Mana/Price', 'Where to Buy'],
    ['Small Mana Potion', '150', '4', '37,5', 'Ginkgo'],
    ['Strong Mana Potion', '300', '12', '25', 'Bicheon'],
    ['Great Mana Potion', '600', '36', '16,66666667', 'Snake Pit']
]

# TODO Numbers should be int, not str? In other words, 'sample' shouldn't exist
sample = [
    ['Name', 'Mana', 'Price', 'Mana/Price', 'Where to Buy'],
    ['Small Mana Potion', 150, 4, 37.5, 'Ginkgo'],
    ['Strong Mana Potion', 300, 12, 25, 'Bicheon'],
    ['Great Mana Potion', 600, 36, 16.66666667, 'Snake Pit']
]

sorted1 = [
    ['Name', 'Mana', 'Price', 'Mana/Price', 'Where to Buy'],
    ['Great Mana Potion', '300', '36', '16,66666667', 'Snake Pit'],
    ['Strong Mana Potion', '300', '12', '25', 'Bicheon'],
    ['Small Mana Potion', '150', '4', '37,5', 'Ginkgo'],
]

sorted2 = [
    ['Name', 'Mana', 'Price', 'Mana/Price', 'Where to Buy'],
    ['Small Mana Potion', '150', '4', '37,5', 'Ginkgo'],
    ['Strong Mana Potion', '300', '12', '25', 'Bicheon'],
    ['Great Mana Potion', '300', '36', '16,66666667', 'Snake Pit'],
]


def test_authentication():
    """
    Attempts to login using the given google credentials and access a particular spreadsheet.
    Then, it checks if it can read first cell of the sheet.

    Performs:
        (Authentication),
        get_cell()
    """
    bot = BotGoogleSheetsPlugin(cur_path + '/client_secret.json', "1kSDXLt7VRBQkGmv0SqCGssYJvGzC1wTUE9qQ-P8fp5w")
    assert bot.get_cell('A', 1) == 'AC'
    assert bot.get_spreadsheet_id() == "1kSDXLt7VRBQkGmv0SqCGssYJvGzC1wTUE9qQ-P8fp5w"
    assert bot.get_spreadsheet_link() == "https://docs.google.com/spreadsheets/d/" \
           + "1kSDXLt7VRBQkGmv0SqCGssYJvGzC1wTUE9qQ-P8fp5w/edit?ouid=107180060500469868309"


def test_read():
    """
    Read tests.

    Performs:
        (Authentication),
        get_cell(),
        get_row(),
        get_column(),
        get_range(),
        as_list()
    """
    bot = BotGoogleSheetsPlugin(cur_path + '/client_secret.json', '1ixNV1rfUBdPO_nCyyq0fYMw_E65feagc_UkWztBNToI')
    assert bot.get_cell('D', 3) == '25'  # TODO Numbers should be int, not str?
    assert bot.get_row(3) == reference[2]
    assert bot.get_column('C') == [row[2] for row in reference]
    assert bot.get_range('B2:C4') == [row[1:3] for row in reference[1:4]]
    assert bot.as_list() == reference


def test_write():
    """
    Write tests.

    Performs:
        (Authentication),
        add_row(),
        add_rows(),
        add_column(),
        add_columns(),
        as_list(),
        clear()
    """
    bot = BotGoogleSheetsPlugin(cur_path + '/client_secret.json', '1wZWG_wOWULUreZofs1r9FFyH_z6m5C5FbYgf01orH9s')
    assert bot.clear().as_list() == []
    assert bot.add_row(sample[0][:2]).as_list() == [reference[0][:2]]
    assert bot.add_rows([row[:2] for row in sample[1:]]).as_list() == [row[:2] for row in reference]
    assert bot.add_column([row[2] for row in sample]).as_list() == [row[:3] for row in reference]
    assert bot.add_columns([[row[3] for row in sample], [row[4] for row in sample]]).as_list() == reference


def test_modify():
    """
    Modify tests.

    Performs:
        (Authentication),
        clear(),
        set_range(),
        set_cell(),
        sort(),
        sort(multiple columns),
        as_list()
    """
    bot = BotGoogleSheetsPlugin(cur_path + '/client_secret.json', '1ozAYIx9B-XzCutdTp7DUIGZq8_5vZfY3o9gcCzeUcIQ')
    bot.clear('Página1').clear('New Sheet')
    assert bot.set_range(sample).as_list() == reference
    assert bot.set_cell('B', 4, 300).get_cell('B', 4) == '300'
    assert bot.set_cell('A', 1, 'AC', 'New Sheet').get_cell('A', 1, 'New Sheet') == 'AC'
    assert bot.sort('C', False).as_list() == sorted1
    assert bot.sort(['B', 'C'], True).as_list() == sorted2


def test_destroy():
    """
    Test

    Performs:
        (Authentication),
        set_range(),
        clear_range(),
        remove_row(),
        remove_rows(),
        remove_column(),
        remove_columns(),
        as_list(),
        clear()
    """
    bot = BotGoogleSheetsPlugin(cur_path + '/client_secret.json', '1DA8LqaANUDf-oqgA2jpMKUNbTpkooa8mKEzjOA2LQWs')
    assert bot.set_range(sample).as_list() == reference
    assert bot.clear_range('A1:B1').get_row(1) == ['', '', 'Price', 'Mana/Price', 'Where to Buy']
    assert bot.remove_row(1).as_list() == reference[1:]
    assert bot.remove_rows([1, 2]).as_list() == [reference[3]]
    assert bot.remove_column('A').as_list() == [reference[3][1:]]
    assert bot.remove_columns(['C', 'D']).as_list() == [reference[3][1:3]]
    assert bot.clear().as_list() == []


def test_sheets():
    """
    Tests with different sheets.

    Performs:
        (Authentication),
        list_sheets(),
        create_sheet(),
        set_active_sheet(new sheet),
        clear(new sheet),
        get_cell(new sheet),
        set_cell(new sheet)
        remove_sheet()

    """
    # Init
    bot = BotGoogleSheetsPlugin(cur_path + '/client_secret.json', '1xR-nwbppy_jVpOg-UxXjbFjJrCGBb4Yn8EI1p9bZJe4')

    # Create sheet
    if bot.list_sheets().count('New Sheet') > 0:
        bot.remove_sheet('New Sheet')
    assert bot.create_sheet('New Sheet').list_sheets().count('New Sheet') > 0

    # Set Active Sheet
    bot.set_active_sheet('New Sheet')
    assert bot.set_cell('A', 1, 'AC').get_cell('A', 1) == 'AC'
    assert bot.clear().as_list() == []

    # Sheet as Parameter
    bot.set_active_sheet()
    assert bot.set_cell('A', 1, 'AC', 'New Sheet').get_cell('A', 1, 'New Sheet') == 'AC'
    assert bot.clear('New Sheet').as_list('New Sheet') == []

    # Remove Sheet
    assert bot.remove_sheet('New Sheet').list_sheets().count('New Sheet') == 0


def test_spreadsheets():
    """
    Spreadsheet management tests.

    Performs:
        create_spreadsheet(),
        set_cell(),
        as_list()
    """
    bot = BotGoogleSheetsPlugin.new_spreadsheet(cur_path + '/client_secret.json', 'Test Spreadsheet')
    assert bot.set_cell('A', 1, 'AC').as_list() == [['AC']]
