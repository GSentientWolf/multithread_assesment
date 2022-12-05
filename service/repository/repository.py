
""" Create and initialize a relational Repository """
import os
import time
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Union
from service.repository.message import Message
from utils.network import Network

START_STOP_WAIT = 1.5
REPOSITORY_INTERVAL = 0.5

class Repository(threading.Thread):
    """
    Base class for Repository
    """
    def __init__(self, *, name: str, thread_name: str):
        super().__init__(name=thread_name, daemon=True, target=self.run)
        self.repo_name = name

    def notifyme(self) -> None:
        pass

    def save(self):
        pass


class FileRepository(Repository):

    def __init__(self, *, location: str, network: Network) -> None:
        super().__init__(name='FileRepository', thread_name='FileArchive')
        fullpath = os.path.abspath(location)
        head_tail = os.path.split(fullpath)
        if os.path.exists(fullpath):
            self.repo_dir = head_tail[0]
            self.repo_name = head_tail[1]
        elif all(head_tail):
            self.repo_dir = head_tail[0]
            self.repo_name = head_tail[1]
        elif head_tail[0] and not head_tail[1]:
            self.repo_dir = head_tail[0]
            self.repo_name = "default_file_repo.txt"
        else:
            self.repo_dir = os.getcwd()
            self.repo_name = head_tail[1]
        self.fullpath = os.path.join(self.repo_dir, self.repo_name)
        # Function exchange between network and repository
        self.network = network
        self.get = network.connect_repository(self.notifyme)
        self.messages = []
        self.new_messages = threading.Event()
        self.is_running = threading.Event()
        self.lock = threading.Lock()

    def start_repository(self) -> None:
        if not self.is_alive():
            # Activate the thread
            print(f'Starting the thread: {self.name}')
            self.start()
            self.is_running.set()
            time.sleep(START_STOP_WAIT)
            return
        print(f'The thread {self.name} is already running!')

    def stop_repository(self) -> None:
        if not self.is_alive():
            return
        self.is_running.clear()
        self.join(1.5 * REPOSITORY_INTERVAL)
        if self.is_alive():
            print(f'Thread {self.name} is still running!')
        else:
            print(f'Thread {self.name} has stopped!')

    def notifyme(self) -> None:
        print("Network notification. Get messages")
        with self.lock:
            self.messages = self.get()

        for message in self.messages:
            print(message)
        self.save()
        return

    def save(self) -> None:
        self.new_messages.set()

    def run(self):
        with open(self.fullpath, "+a") as f:
            while self.is_running.is_set():
                self.new_messages.wait()
                for message in self.messages:
                    print(message)
                    f.write(str(message) + '\n')
                self.new_messages.clear()


class DBRepository(Repository):
    """
        Repository with a simple relational DB
    """
    def __init__(self, *, name: str, db: str = 'sqlite:///sensors.sqlite'):
        super().__init__(name=name)
        self.engine = create_engine(db)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        Message.metadata.create_all(self.engine)

    def add_message(self, message: Message) -> None:
        self.session.add(message)

    def save(self) -> None:
        pass
        # if isinstance(messages, list):
        #     try:
        #         for msg in messages:
        #             self.add_message(msg)
        #     except SQLAlchemyError:
        #         self.session.rollback()
        #         print(f'Last repository session rolled back!')
        #     else:
        #         self.session.commit()
        # else:
        #     self.add_message(messages)
        #     self.session.commit()


if __name__ == '__main__':

    test = 'this is just a simple test for of functionality'.split(' ')
    fileDB = FileRepository(location="./testfile.txt", network=Network())
    fileDB.save()
