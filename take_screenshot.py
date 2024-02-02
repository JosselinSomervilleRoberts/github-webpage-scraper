from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from enum import Enum

from typing import List, Optional, Any, Union
from abc import ABC, abstractmethod
import random


def init_driver(url: str = "http://localhost:4000") -> webdriver.Chrome:
    # Initialize the WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Optional: run in headless mode
    options.add_argument("--no-sandbox")  # Optional: for certain environments
    options.add_argument(
        "--disable-dev-shm-usage"
    )  # Optional: overcome limited resource problems
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    return driver


# Function to find all clickable IDs
def find_clickable_elts(driver: webdriver.Chrome) -> List[str]:
    clickable_elements = driver.find_elements(
        By.XPATH, "//*[@href and (self::a or self::button)]"
    )
    clickable_ids = [
        element.get_attribute("href")
        for element in clickable_elements
        if element.is_displayed()
    ]
    return clickable_ids


def filter_clickable_elts(clickable_ids: List[str]) -> List[str]:
    # 1. Remove duplicates
    clickable_ids = list(set(clickable_ids))

    # 2. Remove empty strings
    clickable_ids = [id for id in clickable_ids if id]

    # 3. Remove non-URLs
    clickable_ids = [id for id in clickable_ids if id.startswith("http")]

    # 4. Remove URLs that are not part of the website
    clickable_ids = [id for id in clickable_ids if "localhost:4000" in id]

    return clickable_ids


class ActionType(Enum):
    """An enumeration to describe the type of action"""

    CLICK = "click"
    SCROLL = "scroll"
    HOVER = "hover"


class Action(ABC):
    """A class to describe an action that a user can perform on a website"""

    def __init__(self, action_type: ActionType, argument: Optional[Any] = None):
        self.action_type = action_type
        self.argument = argument

    @abstractmethod
    def perform(self, driver: webdriver.Chrome):
        pass

    @staticmethod
    def get_random_action(driver: webdriver.Chrome):
        """Randomly choose an action type and return its get_random_action result"""
        action_classes: List["Action"] = [ClickAction, ScrollAction]
        chosen_action_class = random.choice(action_classes)
        return chosen_action_class.get_random_action(driver)

    def __repr__(self) -> str:
        return f"Action({self.action_type}, {self.argument})"

    def __eq__(self, action: "Action") -> bool:
        return (self.action_type == action.action_type) and (
            self.argument == action.argument
        )

    def __hash__(self):
        return hash((self.action_type, self.argument))


class ClickAction(Action):
    """A class to describe a click action"""

    def __init__(self, argument: str):
        super().__init__(action_type=ActionType.CLICK, argument=argument)

    def perform(self, driver: webdriver.Chrome):
        # Go to link provided as argument
        driver.get(self.argument)

    @staticmethod
    def get_random_action(driver: webdriver.Chrome) -> "ClickAction":
        """Get a random click action"""
        clickables: List[str] = filter_clickable_elts(find_clickable_elts(driver))
        link: str = random.choice(clickables)
        return ClickAction(argument=link)


class ScrollAction(Action):
    """A class to describe a scroll action"""

    BOTTOM: str = "bottom"
    TOP: str = "top"

    def __init__(self, argument: Union[int, str]):
        super().__init__(action_type=ActionType.SCROLL, argument=argument)

    def perform(self, driver: webdriver.Chrome):
        if isinstance(self.argument, int):
            driver.execute_script(f"window.scrollBy(0, {self.argument})")
        elif self.argument == self.BOTTOM:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        elif self.argument == self.TOP:
            driver.execute_script("window.scrollTo(0, 0)")

    @staticmethod
    def get_random_action(driver: webdriver.Chrome) -> "ScrollAction":
        """Get a random scroll action"""
        options: List[str] = [ScrollAction.BOTTOM, ScrollAction.TOP, "random"]
        option: str = random.choice(options)
        if option == "random":
            max_scroll_height: int = driver.execute_script(
                "return document.body.scrollHeight"
            )
            return ScrollAction(argument=random.randint(0, max_scroll_height))
        return ScrollAction(argument=option)


if __name__ == "__main__":
    driver = init_driver()
    num_actions = 3
    delay_between_each_action_ms: int = 1000
    actions: List[Action] = [
        Action.get_random_action(driver) for _ in range(num_actions)
    ]
    actions = list(set(actions))
    for action in actions:
        print(f"Performing action: {action}")
        action.perform(driver)
        time.sleep(delay_between_each_action_ms / 1000)

    # Take a screenshot of the page
    driver.save_screenshot("screenshot.png")

    # Close the driver after your operations
    driver.quit()
