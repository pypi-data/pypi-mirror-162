import time
from typing import Optional, Union


class UiProvider:
    """Абстрактный класс представляющий ввод пользователя"""

    def get(self) -> Optional[str]:
        raise NotImplementedError()


class ConsoleUiProvider(UiProvider):
    """Конкретный класс представляющий ввод пользователя из консоли"""

    def get(self) -> Optional[str]:
        try:
            return input()
        except KeyboardInterrupt:
            return None


class MockUiProvider(UiProvider):
    """Конкретный класс симулирующий ввод пользователя из массива"""

    # Строка означает сообщение введенное пользователем, число -- количество секунд которое в течение которого объект
    # будет спать перед тем как интерпретировать следующее действие
    actions: list[Union[str, float]]
    i: int

    def __init__(self, actions: list[Union[str, float]]):
        self.actions = actions
        self.i = 0

    def get(self) -> Optional[str]:
        # Итерация по массиву с выполнением действий
        while True:
            if self.i >= len(self.actions):
                return None
            action = self.actions[self.i]

            if isinstance(action, int) or isinstance(action, float):
                time.sleep(action)
                self.i += 1
            elif isinstance(action, str):
                result = self.actions[self.i]
                self.i += 1
                return result
            else:
                raise ValueError()
