import scrapy
import os
import errno

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'http://renjian.163.com/special/renjian_haodu'
        ]

        for url in urls:
            for i in range(1, 11):
              if i == 1:
                  yield scrapy.Request(url=url, callback=self.parse)
              else:
                  yield scrapy.Request(url="%s_%02d/" % (url, i), callback=self.parse)
        
    def parse(self, response):
        foldername = response.url.split("/")[-2]
        split = foldername.split("_")
        if len(split) == 3:
            split.pop(2)
            foldername = "_".join(split)

        for next in response.css('a::attr(href)').re(r'http://renjian.163.com/\d+/\d+/\d+/[a-zA-Z\d]+.html'):
            self.log("Next page url %s" % next)
            request = response.follow(url=next, callback=self.prcocess_item)
            request.meta['foldername'] = foldername
            yield request

    def prcocess_item(self, response):
        foldername = response.meta['foldername']
        self.save_file(response, foldername)

    def save_file(self, response, foldername):
        filename = response.css("head title::text").extract_first()
        filename = '%s/%s.html' % (foldername, filename)
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        


        