import random
from tinydb import TinyDB, Query


class BullAndCows:
    """Bulls and Cows class for Telegram bot game"""

    def __init__(self):

        self.size = 4
        self.digits = "0123456789"
        self.test = False

        self.start_message = """
I have chosen a number from %s unique digits from 0 to 9 arranged in a random order.
You need to input a %i digit, unique digit number as a guess at what I have chosen
        """ % (self.size, self.size)
        self.help = """
Bot comes up with a four-digit number.
User enters a presumptive number and then receives in response the number of cows and the number of bulls.
(You also need to enter a number from different digits).
BULL: this is a number that is present both in the user number and in the intended number and occupies the same position (order in number).
For example, in numbers 1325 and 9823, the number two is a bull.
COW: This is a number that is present in both numbers but occupies different positions.
        """
        self.__db = TinyDB("chat.json")
        self.__chat = Query()

    @property
    def __set_secret(self):
        """Generates random secret number using provided digits and size
        Returns:
            str: random secret number
        """
        if not self.test:
            return "".join(random.sample(self.digits, self.size))
        else:
            return "1234"

    def get_secret(self, chat_id) -> str:
        """Gets from database chat record secret number.
        Args:
            chat_id:

        Returns:

        """
        secret = ""
        chat = self.__db.get(self.__chat.id == chat_id)
        if chat is not None and chat.get("secret"):
            secret = chat.get("secret")
        return secret

    def __set_win(self, chat_id):
        """Set Win status in database for chat record
        Args:
            chat_id:
        """
        chat = self.__db.get(self.__chat.id == chat_id)
        if chat:
            self.__db.update(
                {"win": True},
                self.__chat.id == chat_id
            )

    def get_win(self, chat_id) -> bool:
        """Gets Win status for chat from database
        Args:
            chat_id: Telegram chat id

        Returns:
            bool: Win status

        """
        win = False
        chat = self.__db.get(self.__chat.id == chat_id)
        if chat:
            win = chat.get("win", False)
        return win

    def __set_attempts(self, chat_id) -> int:
        """Sets number of guessed attempts in database for chat record
        Args:
            chat_id: Telegram chat Id

        Returns:
            int: Number of attempts

        """
        chat = self.__db.get(self.__chat.id == chat_id)
        attempts = 0
        if chat:
            attempts = chat.get("attempts", 0) + 1
            self.__db.update(
                {"attempts": attempts},
                self.__chat.id == chat_id
            )

        return attempts

    def get_attempts(self, chat_id) -> int:
        """Gets number of guessing attempts from database
        Args:
            chat_id: Telegram chat_id
        Returns:
            int: Number of attempts
        """
        attempts = 0
        chat = self.__db.get(self.__chat.id == chat_id)
        if chat:
            attempts = chat.get("attempts", 0)

        return attempts

    def start_game(self, chat_id) -> str:
        """Starts game by inserting db chat row secret random value
        Args:
            chat_id: Telegram chat id

        Returns:
            str: Start message
        """

        chat = self.__db.get(self.__chat.id == chat_id)
        if not chat:
            self.__db.insert(
                {
                    "id": chat_id,
                    "secret": self.__set_secret,
                    "attempts": 0,
                    "win": False
                }
            )

        return self.start_message

    def reset_game(self, chat_id):
        """Removes chats records from database
        Args:
            chat_id: Telegram chat id
        """
        chat = self.__db.get(self.__chat.id == chat_id)
        if chat:
            self.__db.remove(self.__chat.id == chat_id)

    def restart_game(self, chat_id):
        """Restarts game by updating db chat row secret to new random value
        Args:
            chat_id: Telegram chat id
        """
        chat = self.__db.get(self.__chat.id == chat_id)
        if chat:
            self.__db.update(
                {
                    "secret": self.__set_secret,
                    "attempts": 0,
                    "win": False
                },
                self.__chat.id == chat_id
            )

    def validate(self, guess: str) -> bool:
        """Validates guessed number
        Args:
            guess(str): Guessed number

        Returns:
            bool: True if guessed number is valid

        """
        is_size = len(guess) == self.size
        is_digit = all(char in self.digits for char in guess)
        is_unique = len(set(guess)) == self.size

        return is_size and is_unique and is_digit

    def get_bull_and_cows(self, guess: str, secret: str) -> (int, int):
        """Gets count of Bull and Cows
        Args:
            guess(str): Guessed number
            secret(str): Secret number

        Returns:
            int,int: Bulls and Cows
        """
        bulls = cows = 0
        for i in range(self.size):
            if guess[i] == secret[i]:
                bulls += 1
            elif guess[i] in secret:
                cows += 1
        return bulls, cows

    def set_bull_and_cows_message(self, bulls: int, cows: int) -> str:
        """Sets Bull and Cows message
        Args:
            bulls(int): number of bulls
            cows(int): number of cows

        Returns:
            str: "%s Bull and %Cows"
        """
        bull = "🐂"
        cow = "🐄"
        text = []
        text.append(bull*bulls+cow*cows+"\n")
        text.append("%s Bull" % bulls) if bulls == 1 else ""
        text.append("%s Bulls" % bulls) if bulls > 1 else ""
        text.append(" and ") if bulls and cows else ""
        text.append("%s Cow" % cows) if cows == 1 else ""
        text.append("%s Cows" % cows) if cows > 1 else ""
        if not bulls and not cows:
            text.append("%s Bulls and %s Cows" % (bulls, cows))

        return "".join(text)

    def get_win_message(self, chat_id):
        attempts = self.get_attempts(chat_id)
        answer = self.get_secret(chat_id)
        star = "⭐"
        stars = star * (11 - attempts)
        return "<b>You won with answer %s!!!🏆</b>\nNumber of attempts: %s.\n%s" % (answer, attempts, stars)

    def guess(self, guess: str, chat_id: str) -> (str, bool):
        """Game processing guessed number
        Args:
            guess(str): Guessed text
            chat_id(str): Telegram chat id

        Returns:
            (str, bool): Game message, Validation
        """
        secret = self.get_secret(chat_id)
        validate = self.validate(guess)
        if validate:
            self.__set_attempts(chat_id)
            if guess == secret:
                self.__set_win(chat_id)
                return "WIN!!!", validate
            bull, cows = self.get_bull_and_cows(guess, secret)

            message = self.set_bull_and_cows_message(bull, cows)

            return message, validate
        else:
            message = "Problem, try again. You need to enter %i unique digits from 0 to 9" % self.size
            return message, validate
