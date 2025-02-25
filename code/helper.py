import re
import json
import os
from datetime import datetime

with open('variables.json') as variables:
    variables_data = json.load(variables)

spend_categories = variables_data["variables"]["spend_categories"]
choices = variables_data["variables"]["choices"]
plot = variables_data["variables"]["plot"]
spend_display_option = variables_data["variables"]["spend_display_option"]
spend_estimate_option = variables_data["variables"]["spend_estimate_option"]
update_options = variables_data["variables"]["update_options"]
budget_options = variables_data["variables"]["budget_options"]
budget_types = variables_data["variables"]["budget_types"]
data_format = variables_data["variables"]["data_format"]
category_options = variables_data["variables"]["category_options"]
commands = variables_data["variables"]["commands"]
dateFormat = variables_data["variables"]["dateFormat"]
timeFormat = variables_data["variables"]["timeFormat"]
monthFormat = variables_data["variables"]["monthFormat"]

# function to load .json expense record data
def read_json():
    try:
        if not os.path.exists('expense_record.json'):
            with open('expense_record.json', 'w') as json_file:
                json_file.write('{}')
            return json.dumps('{}')
        elif os.stat('expense_record.json').st_size != 0:
            with open('expense_record.json') as expense_record:
                expense_record_data = json.load(expense_record)
            return expense_record_data

    except FileNotFoundError:
        print("---------NO RECORDS FOUND---------")

# function to write the expense record
def write_json(user_list):
    try:
        with open('expense_record.json', 'w') as json_file:
            json.dump(user_list, json_file, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        print('Sorry, the data file could not be found.')

# function to validate the entered amount
def validate_entered_amount(amount_entered):
    if amount_entered is None:
        return 0
    if re.match("^[1-9][0-9]{0,14}\\.[0-9]*$", amount_entered) or re.match("^[1-9][0-9]{0,14}$", amount_entered):
        amount = round(float(amount_entered), 2)
        if amount > 0:
            return str(amount)
    return 0

# function to validate the entered duration
def validate_entered_duration(duration_entered):
    if duration_entered is None:
        return 0
    if re.match("^[1-9][0-9]{0,14}", duration_entered):
        duration = int(duration_entered)
        if duration > 0:
            return str(duration)
    return 0

# function to get user history
def getUserHistory(chat_id):
    data = getUserData(chat_id)
    if data is not None:
        return data['data']
    return None

# function to get user data
def getUserData(chat_id):
    user_list = read_json()
    if user_list is None:
        return None
    if (str(chat_id) in user_list):
        return user_list[str(chat_id)]
    return None

# function to throw exception
def throw_exception(e, message, bot, logging):
    logging.exception(str(e))
    bot.reply_to(message, 'Oh no! ' + str(e))

# function to create a new user record
def createNewUserRecord():
    return data_format

# function to get overall budget
def getOverallBudget(chatId):
    data = getUserData(chatId)
    if data is None:
        return None
    return data['budget']['overall']

# function to get category based budget
def getCategoryBudget(chatId):
    data = getUserData(chatId)
    if data is None:
        return None
    return data['budget']['category']

# function to get category by category
def getCategoryBudgetByCategory(chatId, cat):
    if not isCategoryBudgetByCategoryAvailable(chatId, cat):
        return None
    data = getCategoryBudget(chatId)
    return data[cat]

# function to can add budget
def canAddBudget(chatId):
    return (getOverallBudget(chatId) is None) and (getCategoryBudget(chatId) is None)

# function to check if overall budget available or not
def isOverallBudgetAvailable(chatId):
    return getOverallBudget(chatId) is not None

# function to check if category budget available or not
def isCategoryBudgetAvailable(chatId):
    return getCategoryBudget(chatId) is not None

# function to check if category budget by category available or not
def isCategoryBudgetByCategoryAvailable(chatId, cat):
    data = getCategoryBudget(chatId)
    if data is None:
        return False
    return cat in data.keys()

# function to display remaining budget
def display_remaining_budget(message, bot, cat):
    chat_id = message.chat.id
    if isOverallBudgetAvailable(chat_id):
        display_remaining_overall_budget(message, bot)
    elif isCategoryBudgetByCategoryAvailable(chat_id, cat):
        display_remaining_category_budget(message, bot, cat)

# function to display remaining overall budget
def display_remaining_overall_budget(message, bot):
    print('here')
    chat_id = message.chat.id
    remaining_budget = calculateRemainingOverallBudget(chat_id)
    print("here", remaining_budget)
    if remaining_budget >= 0:
        msg = '\nRemaining Overall Budget is $' + str(remaining_budget)
    else:
        msg = '\nBudget Exceded!\nExpenditure exceeds the budget by $' + str(remaining_budget)[1:]
    bot.send_message(chat_id, msg)

# function to calculate remaining overall budget
def calculateRemainingOverallBudget(chat_id):
    budget = getOverallBudget(chat_id)
    history = getUserHistory(chat_id)
    query = datetime.now().today().strftime(getMonthFormat())
    queryResult = [value for index, value in enumerate(history) if str(query) in value]

    return float(budget) - calculate_total_spendings(queryResult)

# function to calculate total spending
def calculate_total_spendings(queryResult):
    total = 0

    for row in queryResult:
        s = row.split(',')
        total = total + float(s[2])
    return total

# function to display remaining category budget
def display_remaining_category_budget(message, bot, cat):
    chat_id = message.chat.id
    remaining_budget = calculateRemainingCategoryBudget(chat_id, cat)
    if remaining_budget >= 0:
        msg = '\nRemaining Budget for ' + cat + ' is $' + str(remaining_budget)
    else:
        msg = '\nBudget for ' + cat + ' Exceded!\nExpenditure exceeds the budget by $' + str(abs(remaining_budget))
    bot.send_message(chat_id, msg)

# function to calculate remaining category based budget
def calculateRemainingCategoryBudget(chat_id, cat):
    budget = getCategoryBudgetByCategory(chat_id, cat)
    history = getUserHistory(chat_id)
    query = datetime.now().today().strftime(getMonthFormat())
    queryResult = [value for index, value in enumerate(history) if str(query) in value]

    return float(budget) - calculate_total_spendings_for_category(queryResult, cat)

# function to calculate total spending per category
def calculate_total_spendings_for_category(queryResult, cat):
    total = 0

    for row in queryResult:
        s = row.split(',')
        if cat == s[1]:
            total = total + float(s[2])
    return total

# function to get spending categories
def getSpendCategories():
    # with open("categories.txt", "r") as tf:
    #     spend_categories = tf.read().split(',')
    return spend_categories

# function to get plot
def getplot():
    return plot

# function to display spend options
def getSpendDisplayOptions():
    return spend_display_option

# function to get spend estimations
def getSpendEstimateOptions():
    return spend_estimate_option

# function to fetch commands
def getCommands():
    return commands

# function to fetch date format
def getDateFormat():
    return dateFormat

# function to fetch time format
def getTimeFormat():
    return timeFormat

# function to fetch month format
def getMonthFormat():
    return monthFormat

# function to fetch choices
def getChoices():
    return choices

# function to fetch budget options
def getBudgetOptions():
    return budget_options

# function to fetch budget types
def getBudgetTypes():
    return budget_types

# function to update options
def getUpdateOptions():
    return update_options

# function to fetch category options
def getCategoryOptions():
    return category_options
