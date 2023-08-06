from typing import Dict, Callable, List, Optional


class Documents:
    def __init__(self, faker: Callable, index_name: str, batch_size: Optional[int] = 100) -> None:
        """
        Generate documents. 

        :param faker: Faker object for randomization of document values.
        :param index_name: A name of index that must be used for indexing of the documents.
        :param batch_size: [Optional, default=100] A size of documents batch. 

        :return: No return.
        """

        self.__faker = faker
        self.__index_name = index_name
        self.__batch_size = batch_size
        self.documents = self.__make_documents()

    def document_action(self, action: str) -> Dict[str, str]:
        """
        Iterate a collection of random generated documents and return OpenSearch bulk action compatible dictionary.

        :param action: String representation of OpenSearch action. Possible actions: create | update | delete | index

        :return: A dictionary compatible with OpenSearch bulk action. 
        """

        for document in self.documents:

            yield {
                '_op_type': action,
                '_index': self.__index_name,
                '_id': document['id'],
                '_source': document
            }

    def __make_documents(self) -> List[Dict[str, str]]:
        """
        Make a collection of random value documents.

        :return: A list of documents in a dictionary format.
        """

        return [
            {
                'id': self.__faker.uuid4(),
                'author': f'{self.__faker.first_name()} {self.__faker.last_name()}',
                'title': self.__faker.text(),
                'description': self.__faker.text(),
                'content': self.__faker.text(),
                'timestamp': self.__faker.date_time().strftime('%Y-%m-%d %H:%M:%S')
            } for _ in range(self.__batch_size)
        ]
