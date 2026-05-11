from src.core.config import settings


def welcome_email(username: str, token: str) -> str:
    """
    Generate a welcome email template for the given username.

    Args:
        username (str): The username of the recipient.

    Returns:
        str: The HTML content of the welcome email.
    """

    return f'''
        <h2>Welcome to Todo App, {username}!</h2>
        <p>Your account has been created successfully.</p>
        <p>Use the token below to verify your email address. <b>It expires in {settings.VERIFICATION_TOKEN_EXPIRE_MINUTES} minutes.</b></p>
        <hr>
        <p>{token}</p>
        <hr>
    '''


def due_date_reminder_email(username: str, data: list[dict]) -> str:
    """
    Generate a due date reminder email template for the given username and task data.

    Args:
        username (str): The username of the recipient.
        data (list[dict]): A list of task dictionaries with 'title' and 'due_date' keys.

    Returns:
        str: The HTML content of the due date reminder email.
    """
    task_list = ''.join(
        [
            f'''
                <li>
                    <strong>{task['title']}</strong>
                    - due {task['due_date']}
                </li>
            '''
            for task in data
        ]
    )

    return f'''
        <h2>Hi {username}, you have tasks due tommorow!</h2>
        <ul>{task_list}</ul>
        <p>Stay on top of your work!</p>
    '''


def password_reset_email(username: str, reset_token: str) -> str:
    """
    Generate a password reset email template for the given username and reset token.

    Args:
        username (str): The username of the recipient.
        reset_token (str): The password reset token to include in the email.

    Returns:
        str: The HTML content of the password reset email.
    """
    return f'''
        <h2>Hi {username}, you requested a password reset.</h2>
        <p>Use the token below to reset your password. It expires in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes and can only be used once!</p>
        <hr>
        <p>{reset_token}</p>
        <hr>
        <p>If you did not request this, you can safely ignore this email.</p>
    '''

def email_change_verification_email(username: str, new_email: str, token: str) -> str:
    return f'''
        <h2>Hi {username}, confirm your new email address.</h2>
        <p>You requested to chage your email to <strong>{new_email}</strong></p>
        <p>Use the token below to confirm. It expires in {settings.VERIFICATION_TOKEN_EXPIRE_MINUTES}.</p>
        <hr>
        <p><strong>{token}</strong></p>
        <hr>
        <p>If you did not request this, you can safely ignore this email.</p>
    '''
