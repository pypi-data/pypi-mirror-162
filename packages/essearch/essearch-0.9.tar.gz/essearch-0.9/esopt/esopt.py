# elasticsearch的初始化

from pprint import pprint
import ijson
from tqdm import tqdm
from elasticsearch import Elasticsearch

# 以下路径本机和服务器中不同
json_path = ["/data2/dengyunlong/wiki_cn_data.json", "D:/My_Apps/BaiduNetdiskDownload/563w_baidubaike.json"
                                                     "/563w_baidubaike.json"]


def max_min(x: float, num_max: float, num_min: float):
    x = (x - num_min) / (num_max - num_min + 0.01)
    return x


# 下面服务器中不需要用户名和密码的设置
def es_start(es_url="http://localhost:9200"):
    global es
    es = Elasticsearch([es_url], timeout=3600)


# 创建索引
def create_mapping(index: str):
    body = {
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "url": {
                    "type": "text"
                },
                "article": {
                    "type": "text",
                    "analyzer": "ik_smart"
                },
                "wiki_id": {
                    "type": "text"
                }
            }
        }
    }
    es.indices.create(index=index, body=body)


# 创建索引(便于从MySQL直接导入数据的索引)
def create_mapping_mysql(index: str):
    body = {
        "mappings": {
            "properties": {
                "es_id": {
                    "type": "text"
                },
                "url": {
                    "type": "text"
                },
                "title": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "content": {
                    "type": "text",
                    "analyzer": "ik_smart"
                },
                "author": {
                    "type": "text"
                },
                "publish_time": {
                    "type": "date",
                    "format": "yyyy-MM-dd HH:mm:ss"
                },
                "filename": {
                    "type": "text"
                },
                "create_time": {
                    "type": "date",
                    "format": "yyyy-MM-dd HH:mm:ss"
                },
                "update_time": {
                    "type": "date",
                    "format": "yyyy-MM-dd HH:mm:ss"
                },
                "summary": {
                    "type": "text",
                    "analyzer": "ik_smart"
                },
                "tags": {
                    "type": "text",
                    "analyzer": "ik_smart"
                },
                "attributes": {
                    "type": "text",
                    "analyzer": "ik_smart"
                }
            }
        }
    }
    es.indices.create(index=index, body=body)


# 插入词条
def insert_entry(idx: str, doc: dict):
    es.index(index=idx, body=doc)


# 将json文件转化成elasticsearch接受的doc，并将其全部插入elasticsearch中
def json_to_doc(source: str, index: str):
    print("source:          ", source)
    with open(source, 'r', encoding='utf-8') as f:
        item_list = list(ijson.items(f, ''))[0]
        print(len(item_list))
        for item in tqdm(item_list):
            item_dict = {"wiki_id": item[0], "title": item[1], "url": item[2], "article": item[3]}
            insert_entry(index, item_dict)


# # 查询词条
# def search_entry(index, query: str, min_score=0.0, fields=None, source_includes=None, size=10):
#     """
#     返回一个字典，内容是{ index1 : [{doc1}, {doc2} ...], index2 : [] ...}
#     :param size: int, 返回结果的最大条数
#     :param source_includes: list[str], 返回的字段
#     :param fields: list[str], 参与评分排序的字段
#     :param min_score: float, 返回内容的最小得分
#     :param query: str, 要搜索的字符串
#     :param index: list[str], 选择的索引列表
#     """
#     if source_includes is None:
#         if index == "wiki_cn_new" or index == "wiki_cn":
#             source_includes = ['title', 'article', 'wiki_id', 'url']
#         elif index == "baidubaike":
#             source_includes = ['title', 'article', 'url', 'tags', 'summary']
#         elif index == "baidubaike_new":
#             source_includes = ['title', 'article', 'url']
#         elif index == "baidubaike_spider":
#             source_includes = ['title', 'content', 'url', 'tags', 'summary', 'author', 'publish_time', 'filename', 'website', 'attributes']
#     if fields is None:
#         fields = ['title^5', 'article']
#         if index == "baidubaike":
#             fields = ['title^5', 'article', 'tags^5', 'summary^2']
#         elif index == "baidubaike_spider":
#             fields = ['title^5', 'content', 'summary^2', 'attributes^2']
#     res_list = []
#     analyzer_list = {"wiki_cn_new": "ik_max_word", "wiki_cn": "standard", "baidubaike": "ik_max_word",
#                      "baidubaike_new": "ik_max_word", "baidubaike_spider": "ik_max_word"}
#     resp = es.search(index=index, size=100,
#                      query={
#                          "multi_match": {
#                              "query": query,
#                              "analyzer": analyzer_list[index],
#                              "fields": fields
#                          }
#                      })
#     score_list = []
#     for res in resp['hits']['hits']:
#         if index != "baidubaike_new" and index != "baidubaike_spider":
#             if len(res['_source']['article']) < 20:
#                 res['_score'] = float(res['_score']) / 3.0
#         score_list.append(res['_score'])
#     max_res_score = max(score_list)
#     min_res_score = min(score_list)
#     for res in resp['hits']['hits']:
#         res['_score'] = max_min(res['_score'], max_res_score, min_res_score)
#         res_list.append(res)
#     res_list.sort(key=lambda x: (x['_score']), reverse=True)
#     final_res_list = []
#     size_num = 0
#     for res in res_list:
#         size_num += 1
#         if res['_score'] >= min_score and size_num <= size:
#             final_res = {}
#             for item in source_includes:
#                 final_res.update({item: res['_source'][item]})
#             final_res_list.append(final_res)
#     return final_res_list

# 查询词条
def search_entry(query: str, index, min_score=0.0, fields=None, source_includes=None, size=10):
    """
    返回一个字典，内容是{ index1 : [{doc1}, {doc2} ...], index2 : [] ...}
    :param size: int, 返回结果的最大条数
    :param source_includes: list[str], 返回的字段
    :param fields: list[str], 参与评分排序的字段
    :param min_score: float, 返回内容的最小得分
    :param query: str, 要搜索的字符串
    :param index: list[str], 选择的索引列表
    """
    if index is None:
        index = ['baidubaike_spider']
    elif not isinstance(index, list):
        index = [index]

    if source_includes is None:
        source_includes = ['title', 'wiki_id', 'article', 'content', 'url', 'tags', 'summary', 'author', 'publish_time',
                           'filename', 'website', 'attributes']

    score_list = []
    res_doc_all_list = []
    res_list = []

    try:
        for item in index:
            res_doc_list = []
            for doc_item in search_entry_single_index(query, item, fields, size):
                res_doc_list.append(doc_item)
                res_doc_all_list.append(doc_item)
            for res in res_doc_list:
                if index != "baidubaike_spider":
                    res['_score'] = float(res['_score']) * float(len(res['_source']['article'])) / (
                            len(res['_source']['article']) + 40)
                elif index == "baidubaike_spider":
                    res['_score'] = float(res['_score']) * float(len(res['_source']['content'])) / (
                            len(res['_source']['content']) + 40)
                score_list.append(res['_score'])

        max_res_score = max(score_list)
        min_res_score = min(score_list)
        for res in res_doc_all_list:
            res['_score'] = max_min(res['_score'], max_res_score, min_res_score)
            res_list.append(res)
        res_list.sort(key=lambda x: (x['_score']), reverse=True)
        final_res_list = []
        size_num = 0
        for res in res_list:
            size_num += 1
            if res['_score'] >= min_score and size_num <= size:
                final_res = {}
                for item in source_includes:
                    try:
                        final_res.update({item: res['_source'][item]})
                    except:
                        pass
                final_res_list.append(final_res)
    except Exception as e:
        print("During searching entry in elasticsearch, an error occurred:         ", e)
        return []
    return final_res_list


def search_entry_single_index(query: str, index: str, fields=None, size=10):
    if fields is None:
        fields = ['title^5', 'article']
        if index == "baidubaike":
            fields = ['title^5', 'article', 'tags', 'summary']
        elif index == "baidubaike_spider":
            fields = ['title^5', 'content', 'summary', 'attributes']

    analyzer_list = {"wiki_cn_new": "ik_max_word", "wiki_cn": "standard", "baidubaike": "ik_max_word",
                     "baidubaike_new": "ik_max_word", "baidubaike_spider": "ik_max_word"}
    resp = es.search(index=index, size=5 * size,
                     query={
                         "multi_match": {
                             "query": query,
                             "analyzer": analyzer_list[index],
                             "fields": fields
                         }
                     })
    return resp['hits']['hits']


if __name__ == '__main__':
    es_start()
    pprint(search_entry(index=["baidubaike", "baidubaike_new"], query="的"))
    # create_mapping_mysql('baidubaike-spider')
    # json_to_doc(json_path[0], 'wiki_cn_new')
    # pprint(search_entry(index='wiki_cn_new', query='上海市的语言', source_includes=['title'], min_score=0.0))
