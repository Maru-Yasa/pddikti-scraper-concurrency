from datetime import datetime

class Logger:
    def __init__(self):
        self.current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.log_file_path = f'log-{datetime.now().strftime("%Y-%m-%d")}.txt'

    def log(self, text) -> None:
        text = f'[{self.current_datetime}] - {text}'
        print(text)
        with open(self.log_file_path, 'a') as log_file:
            log_file.write(f'{text}\n')