from aiogram.fsm.state import StatesGroup, State

class StateGroups:
    class AddSource(StatesGroup):
        username = State()

    class RemoveSource(StatesGroup):
        username = State()

    class SetTarget(StatesGroup):
        username = State()

    class AddSpamKeyword(StatesGroup):
        keyword = State()

    class RemoveSpamKeyword(StatesGroup):
        keyword = State()

    class AddSpamType(StatesGroup):
        type = State()

    class RemoveSpamType(StatesGroup):
        type = State()

    class SetAiModel(StatesGroup):
        model = State()

    class AiPrompt(StatesGroup):
        text = State()
