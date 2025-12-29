from starlette.background import BackgroundTasks
from gui import GUI
import asyncio

gui = GUI()

@gui.app.on_event('startup')
async def app_startup():
	asyncio.create_task(gui.counter.update_state_loop())

def main():
	gui.start(777)

if __name__ == '__main__':
    main()