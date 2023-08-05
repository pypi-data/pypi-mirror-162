import os.path

import re
from selenium import webdriver
from selenium.common.exceptions import JavascriptException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from subprocess import PIPE, Popen
from time import sleep
from typing import List

from dnastack.common.environments import env, flag
from dnastack.common.logger import get_logger


class UnexpectedCommandProcessTerminationError(RuntimeError):
    pass


class UnexpectedLoginError(RuntimeError):
    pass


def handle_device_code_flow(cmd: List[str], email: str, token: str) -> str:
    """ Handle the device code flow """
    logger = get_logger(f'{os.path.basename(__file__)}/handle_device_code_flow')
    re_confirmation_url = re.compile(r'https://[^\s]+/authorize\?user_code=[^\s]+')

    p = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    device_code_url = None
    while device_code_url is None:
        exit_code = p.poll()
        if exit_code is not None:
            logger.error(f'CLI: EXIT: {exit_code}')
            logger.error(f'CLI: STDOUT: {p.stdout.read()}')
            logger.error(f'CLI: STDERR: {p.stderr.read()}')

            raise UnexpectedCommandProcessTerminationError(exit_code)
        try:
            output = p.stdout.readline()
            matches = re_confirmation_url.search(output)

            logger.debug(f'OUTPUT READ: {output}')

            if matches:
                device_code_url = matches.group(0)
                logger.debug('Detected the device code URL')
            else:
                logger.debug('Waiting...')
                sleep(1)
        except KeyboardInterrupt:
            p.kill()
            raise RuntimeError('User terminated')

    logger.debug('Confirming the device code')
    _confirm_device_code(device_code_url, email, token)
    logger.debug('Waiting for the CLI to join back...')

    while True:
        exit_code = p.poll()
        if exit_code is not None:
            break

    output = p.stdout.read()
    error_output = p.stderr.read()

    p.stdout.close()
    p.stderr.close()

    assert exit_code == 0, f'Unexpected exit code {exit_code}:\nSTDOUT:\n{output}\nERROR:\n{error_output}'

    return output


def _confirm_device_code(device_code_url, email: str, token: str, allow=True):
    logger = get_logger(f'{os.path.basename(__file__)}/_confirm_device_code')

    inside_docker_container = bool(
        env('PYTHON_VERSION', required=False)
        and env('PYTHON_SETUPTOOLS_VERSION', required=False)
        and env('PYTHON_PIP_VERSION', required=False)
    )

    asked_for_headless_mode = flag('E2E_HEADLESS')
    use_headless_mode = inside_docker_container or asked_for_headless_mode

    logger.debug(f'webdriver: asked_for_headless_mode => {asked_for_headless_mode}')
    logger.debug(f'webdriver: inside_docker_container => {inside_docker_container}')
    logger.debug(f'webdriver: use_headless_mode => {use_headless_mode}')

    chrome_options = Options()
    chrome_options.headless = use_headless_mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    logger.debug(f'Web driver: Activated')

    driver.get(device_code_url)

    logger.debug(f'Web driver: Go to {device_code_url}')

    try:
        # NOTE: This is invoked on WalletN.
        driver.execute_script(
            f"document.querySelector('form[name=\"token\"] input[name=\"token\"]').value = '{token}';"
            f"document.querySelector('form[name=\"token\"] input[name=\"email\"]').value = '{email}';"
        )
    except JavascriptException as e:
        # Show any information available from the driver.
        logger.error(f'Failed to execute the script on {driver.current_url}.')
        logger.error(f'Here is what the driver can see.\n\n{driver.page_source}\n')
        driver.quit()

        raise UnexpectedLoginError(f'Failed to log in with {email} at {device_code_url} due to JavaScript error ({e})')
    except Exception as e:
        # Show any information available from the driver.
        logger.error(f'Failed to execute the script on {driver.current_url}.')
        logger.error(f'Here is what the driver can see.\n\n{driver.page_source}\n')
        driver.quit()

        raise UnexpectedLoginError(f'Failed to log in with {email} at {device_code_url} due to unexpected error ({e})')

    sleep(5)
    logger.debug(f'Web driver: Current: URL: {driver.current_url}')
    logger.debug(f'Web driver: Current: Source: {driver.page_source}')

    token_form = driver.find_element(By.CSS_SELECTOR, "form[name='token']")
    token_form.submit()

    sleep(2)

    try:
        driver.find_element(By.ID, "continue-btn").click()

        if allow:
            driver.find_element(By.ID, "allow-btn").click()
        else:
            driver.find_element(By.ID, "deny-btn").click()
    except NoSuchElementException:
        # Show any information available from the driver.
        logger.error(f'Failed to execute the script on {driver.current_url}.')
        logger.error(f'Here is what the driver can see.\n\n{driver.page_source}\n')
    finally:
        driver.quit()
        logger.debug(f'Web driver: Deactivated')
