import sys

Command = [
    'help',
    'Maya',
    'Unreal'
]

class Application():
    def __init__(self):
        return

    def run(self):
        for line in sys.stdin:
            print(line)
        return 0
    
    
def main() -> int:
    exit_code: int = Application().run()
    return exit_code