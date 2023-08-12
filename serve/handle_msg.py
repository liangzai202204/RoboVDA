import queue


class MessageHandler:
    def __init__(self):
        # 初始化一个队列来存放消息
        self.messages = queue.Queue()

    def receive_message(self, message):
        # 将消息放入队列
        self.messages.put(message)

    def process_messages(self):
        while not self.messages.empty():
            # 取出一个消息并处理
            message = self.messages.get()
            self.handle_message(message)

    def handle_message(self, message):
        # 这个方法需要根据你的业务逻辑来设计
        # 在这里我只是简单地打印消息
        print(f'处理消息: {message}')