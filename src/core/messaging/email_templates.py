def welcome_email(username: str) -> str:
    return f'''
        <h2>Welcome to Todo App, {username}!</h2>
        <p>Your account has been created successfully.</p>
        <p>You can now log in and start managing your tasks and projects :)</p>
    '''


def due_date_reminder_email(username: str, data: list[dict]) -> str:
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
