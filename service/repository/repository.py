
""" Create and initialize a relational Repository """
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Union
from service.repository.message import Message
from utils.network import Network


class Repository:
    """
    Base class for Repository
    """
    def __init__(self, *, name: str):
        self.repo_name = name

    def receive_notification(self) -> None:
        ...

    def save(self, messages: List[str]):
        ...


class FileRepository(Repository):

    def __init__(self, *, location: str, network: Network) -> None:
        super().__init__(name='FileRepository')
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
        self.get_messages_from_network = network.connect_repository(self.notify)

    def notify(self) -> None:
        messages = self.get_messages_from_network()
        self.save(messages)

    def save(self, messages: List[str]) -> None:
        with open(self.fullpath, "+w") as f:
            for message in messages:
                f.write(message)
                f.write('\n')


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

    def save(self, messages: Union[List[Message] | Message]) -> None:

        if isinstance(messages, list):
            try:
                for msg in messages:
                    self.add_message(msg)
            except SQLAlchemyError:
                self.session.rollback()
                print(f'Last repository session rolled back!')
            else:
                self.session.commit()
        else:
            self.add_message(messages)
            self.session.commit()


if __name__ == '__main__':

    test = 'this is just a simple test for of functionality'.split(' ')
    fileDB = FileRepository(location="./testfile.txt")
    fileDB.save(test)
