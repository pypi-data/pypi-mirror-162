from types import NoneType
from typing import Dict

PROMPTS: Dict[str, str] = {
    "string": "enter a string",
    "integer": "enter an integer",
    "float": "enter a float",
    "boolean": "enter a boolean (true/false)",
    "yesno": "enter yes or no (y/n):",
}


class Input:
    """Holds Methods for asking inputs."""

    @classmethod
    def _construct(cls, type: str, prompt: str | NoneType = None, error: str | NoneType = None) -> str:
        """
        Constructs a prompt, error message.

        Args:
            type (str): type of input.
            prompt (str, optional): prompt message. Defaults to None.
            error (str, optional): error message. Defaults to None.

        Returns:
            List[str]: [prompt, error]
        """
        if not prompt:
            prompt = PROMPTS[type]
        prompt += ": "
        if not error:
            error = f"invalid input for {type}"
        error = f"! {error}"
        return prompt, error

    @classmethod
    def string(cls, prompt: str | NoneType = None) -> str:
        """string

        ask a input from user and return a string.
        (same as input())

        Args:
            prompt (str, optional): prompt message. Defaults to None.

        Returns:
            str: input string.
        """
        prompt, _ = cls._construct(type="string", prompt=prompt)
        return input(prompt)

    @classmethod
    def integer(cls, prompt: str | NoneType = None, error: str | NoneType = None) -> int:
        """integer

        ask a input from user and return an integer.
        (same as int(input()))

        Args:
            prompt (str, optional): prompt message. Defaults to None.
            error (str, optional): error message. Defaults to None.

        Returns:
            int: input integer.
        """
        prompt, error = cls._construct(
            type="integer", prompt=prompt, error=error)
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print(error)

    @classmethod
    def floating_point(cls, prompt: str | NoneType = None, error: str | NoneType = None) -> float:
        """floating_point

        ask a input from user and return a float.
        (same as float(input()))

        Args:
            prompt (str, optional): prompt message. Defaults to None.
            error (str, optional): error message. Defaults to None.

        Returns:
            float: input float.
        """
        prompt, error = cls._construct(
            type="float", prompt=prompt, error=error)
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print(error)

    @classmethod
    def boolean(cls, prompt: str | NoneType = None, error: str | NoneType = None) -> bool:
        """boolean

        ask a input from user and return a boolean.
        (same as bool(input()))

        Args:
            prompt (str, optional): prompt message. Defaults to None.
            error (str, optional): error message. Defaults to None.

        Returns:
            bool: input boolean.
        """
        valid = ['true', 'false']
        prompt, error = cls._construct(
            type="boolean", prompt=prompt, error=error)
        while True:
            boolean = input(prompt).lower()
            if boolean in valid:
                return boolean == 'true'
            else:
                print(error)


if __name__ == "__main__":
    # string
    print(Input.string())
    print(Input.string('string'))

    # integer
    print(Input.integer())
    print(Input.integer('integer', 'wrong'))

    # floating point
    print(Input.floating_point())
    print(Input.floating_point('float', 'wrong'))

    # boolean
    print(Input.boolean())
    print(Input.boolean('boolean', 'wrong'))
