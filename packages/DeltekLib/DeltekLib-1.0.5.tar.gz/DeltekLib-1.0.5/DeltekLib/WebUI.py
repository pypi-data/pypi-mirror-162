# Deltek Python Library
# Copyright 2021

from robot.libraries.BuiltIn import BuiltIn


def input_text_and_wait(txt_locator, text, element_to_wait_for, to_clear=True, wait_time='5s'):
    """
    Types text into the element and waits for an element to be visible before returning

    :param txt_locator: locator for the input element
    :param text: text to be entered in the input element
    :param element_to_wait_for: locator for the element to be visible
    :param to_clear: if true, input element is cleared of any values before the text is typed into the element
    :param wait_time: waits for specified time, defaults to 5 seconds
    :return: none

    *Example*
    | Input Text And Wait | xpath=//elem[@id="InputElement"] | Deltek | xpath=//elem[@id="ElementToWaitFor"]
    """
    BuiltIn().run_keyword("Input Text", txt_locator, text, to_clear)
    BuiltIn().run_keyword("Wait Until Element Is Visible", element_to_wait_for, wait_time)


def wait_before_click(element, timeout='30s'):
    """
    Waits for the element to be visible before performing click event

    :param element: locator for the element to wait before clicking
    :param timeout: waits for specified time, defaults to 30 seconds
    :return: none

    *Example*
    | Wait Before Click | xpath=//elem[@id="ElementToClick"] | timeout=1m
    """
    BuiltIn().run_keyword("Wait Until Element Is Visible", element, timeout)
    BuiltIn().run_keyword("Click Element", element)


def click_then_wait(element, wait_element, timeout='30s'):
    """
    Clicks the element then waits for another element to be visible

    :param element: locator for the element to click
    :param wait_element: locator for the element to wait to be visible
    :param timeout: waits for specified time, defaults to 30 seconds
    :return: none

    *Example*
    | Click Then Wait | xpath=//elem[@id="ElementToClick"] | xpath=//elem[@id="ElementToWaitFor"] | timeout=1m
    """
    BuiltIn().run_keyword("Wait Until Element Is Visible", element, timeout)
    BuiltIn().run_keyword("Click Element", element)
    BuiltIn().run_keyword("Wait Until Element Is Visible", wait_element, timeout)


def input_credentials(txt_username, user_name, txt_password, password, btn_login,
                      to_clear=True, wait_time='5s'):
    """
    Enters user name and password to specified elements

    :param txt_username: locator for User Name field
    :param user_name: User's name
    :param txt_password: locator for Password field
    :param password: User's Password
    :param btn_login: locator for Login Button
    :param to_clear: if true, input element is cleared of any values before the text is typed into the element
    :param wait_time: waits for specified time, defaults to 5 seconds
    :return: none

    *Example*
    | Input Credentials | xpath=//elem[@id="UserName"] | UserName | xpath=//elem[@id="Password"] | Password |
    ...     xpath=//elem[@id="LoginButton"]
    """
    BuiltIn().run_keyword("Input Text With Wait On Next Element", txt_username, user_name, txt_password,
                          to_clear, wait_time)
    BuiltIn().run_keyword("Input Password", txt_password, password)
    BuiltIn().run_keyword("Click Element", btn_login)


def open_browser_maximized(base_url, browser):
    """
    Opens a browser and have it maximized

    :param base_url: base url to open
    :param browser: browser to use in opening the base url
    :return: none

    *Example*
    | Open Browser Maximized | http://deltek.com | chrome
    """
    BuiltIn().run_keyword("Open Browser", base_url, browser)
    BuiltIn().run_keyword("Maximize Browser Window")


def scroll_before_click(element, timeout='1m'):
    """
    Scrolls to the element before clicking

    :param element: locator for the element to wait before clicking
    :param timeout: waits for specified time, defaults to 1 minute
    :return: none
    """
    BuiltIn().run_keyword("Wait Until Element Is Visible", element, timeout)
    BuiltIn().run_keyword("Set Focus To Element", element)
    BuiltIn().run_keyword("Scroll Element Into View", element)
    BuiltIn().run_keyword("Sleep", "0.25s")
    BuiltIn().run_keyword("Click Element", element)
