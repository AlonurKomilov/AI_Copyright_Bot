from aiogram.fsm.state import StatesGroup, State

# States for the Admin Control Panel
class AdminStates(StatesGroup):
    add_source = State()
    remove_source = State()
    set_target = State()
    add_spam_keyword = State()
    remove_spam_keyword = State()
    add_spam_type = State()
    remove_spam_type = State()
    set_ai_model = State()

# States for the PRO user settings
class ProStates(StatesGroup):
    set_target = State()
    add_source = State()
    set_filters = State()
    set_media_types = State()
    set_ai_model = State()

# State for managing conversation history
class Conversation(StatesGroup):
    active = State()
