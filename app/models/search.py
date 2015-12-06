from app import mysql
from app import webapp
from app.models import Item
from elasticsearch import Elasticsearch
import requests
import string

class Search():
    def __init__(self, query, size=20):
        self.es_url  = webapp.config['ES_NODES'].split(',')
        self.es = Elasticsearch(self.es_url)
        self.query = query
        self.index = 'items'
        self.size = size

    def basicSearch(self, page=0):
        data = {
                "query": {
                    "function_score": {
                        "query": {
                            "query_string": {
                                "query": self.query
                                }
                            },
                        "functions": [
                            {
                                "field_value_factor": {
                                    "field": "num_ratings"
                                    }
                                }
                            ]
                        }
                    }
                }
        '''
        data = {
                "query": {
                    "query_string": {
                        "query": self.query
                        }
                    }
                }

        '''
            
        return self.executeSearch(data, page)


    def categorySearch(self, page=0):
        data = {
                "query": {
                    "term": {
                        "categories": self.query
                        }
                    }
                }
        return self.executeSearch(data, page)

    def isbnSearch(self, page=0):
        data = {
                "query": {
                    "term": {
                        "isbn": self.query
                        }
                    }
                }

        return self.executeSearch(data, page)


    def executeSearch(self, data, page):
        search_results = self.es.search(index=self.index, body=data, from_=page*self.size, size=self.size)
        item_results = []
        total_results = 0
        if 'hits' in search_results and search_results['hits']['total']:
            total_results = search_results['hits']['total']
            for item in search_results['hits']['hits']:
                item_results.append(item['_source'])

        final_search_results = {
                "total": total_results,
                "items": item_results
                }

        return final_search_results


    '''
        To call other ES apis directly
        TODO: add data support
    '''
    def customQuery(self):
        resp = requests.get(string.rstrip(self.es_url[0], '/')+'/'+self.query)
        return resp.text

    
    '''
        MySQL searches
    '''
    @staticmethod
    def searchQuery(q, page=1):

        limit = page * 20
        offset = (page-1) *20

        connect = mysql.connect()
        search_cursor = connect.cursor()
        search_cursor.execute("SELECT item_id FROM items WHERE item_name LIKE \
                '%%%s%%' OR author LIKE '%%%s%%' LIMIT %d OFFSET %d" %(q, q, limit, offset))
        results = search_cursor.fetchall()
        search_cursor.close()

        refined_results = []
        for item_id in results:
            item = Item(item_id[0])
            refined_results.append(item.getObj())

        return refined_results

        search_cursor = self.connect.cursor()
        search_cursor.execute("SELECT i.item_id FROM items i \
                        LEFT JOIN items_categories ic ON i.item_id = ic.item_id \
                        LEFT JOIN categories c ON c.category_id = ic.category_id \
                        WHERE c.category_name LIKE '%%%s%%' LIMIT %d" %(q, 200-len(refined_results))) 
        results = search_cursor.fetchall()
        search_cursor.close()

        for item_id in results:
            if len(refined_results) <= 20:
                item = Item(item_id[0])
                refined_results.append(item_id.getObj())

        return refined_results        


    @staticmethod
    def searchQueryByType(q, qtype, page=1):

        limit = page * 20
        offset = (page-1) *20

        if qtype == "title":
            query = "SELECT item_id FROM items WHERE item_name LIKE \
                '%%%s%%' LIMIT %d OFFSET %d"
        elif qtype == "genre":
            query = "SELECT i.item_id FROM items i \
                LEFT JOIN items_categories ic ON i.item_id = ic.item_id \
                LEFT JOIN categories c ON c.category_id = ic.category_id \
                WHERE c.category_name LIKE '%%%s%%' LIMIT %d OFFSET %d"

        connect = mysql.connect()
        search_cursor = connect.cursor()
        search_cursor.execute(query % (q, limit, offset))
        results = search_cursor.fetchall()
        search_cursor.close()

        refined_results = []
        for item_id in results:
            item = Item(item_id[0])
            refined_results.append(item.getObj())


        return refined_results


