import feapder


class XueQiuSpider(feapder.AirSpider):
    def start_requests(self):
        yield feapder.Request("https://baijiahao.baidu.com/s?id=1739368224007714423", render=True)

    def parse(self, request, response):
        print(response)


if __name__ == "__main__":
    XueQiuSpider(thread_count=1).start()
