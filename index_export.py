from opensearchpy import OpenSearch, helpers
import json

def get_source_index_mapping_and_settings(client, index):
    mapping = client.indices.get_mapping(index=index)
    return mapping[index]['mappings']

def create_target_index(client, index, mapping):
    client.indices.create(
        index=index,
        body={
            "mappings": mapping
        }
    )



def export_data(client, index):
    # Use a scroll to fetch all data from the index
    query = {"query": {"match_all": {}}}
    
    results = helpers.scan(
        client=client,
        query=query,
        index=index,
        scroll='2m',  # Time to keep the scroll context alive
        size=1000     # Number of documents per batch
    )
    
    return list(results)


def import_data(client, index, docs):
    actions = []
    for doc in docs:
        # Create a bulk insert action
        action = {
            "_op_type": "index",
            "_index": index,
            "_id": doc['_id'],  # Use the same ID or generate new ones
            "_source": doc['_source']
        }
        actions.append(action)
    
    # Bulk insert into target index
    helpers.bulk(client, actions)

def search_index(client, index, query):
    response = client.search(
                index=index, 
                body=query)
    logs = []
    for hit in response['hits']['hits']:
        logs.append(hit['_source']['message'])
    print(len(response['hits']['hits']))
    return logs


def transport_loghub_index():
    # Initialize OpenSearch client
    source_client = OpenSearch(
        hosts=[{'host': 'opensearch-cluster', 
                'port': 80}],  
        http_auth=('admin', 'admin'),  
    )
    
    target_client = OpenSearch(
        hosts=[{'host': 'opensearch-cluster', 
                'port': 80}],  
        http_auth=('admin', 'admin'),  
    )

    info = source_client.info()
    print(f"Source {info['version']['distribution']} {info['version']['number']}!")
    info = target_client.info()
    print(f"Target {info['version']['distribution']} {info['version']['number']}!")
    
    index_list = ["loghub-zookeeper-new",'loghub-windows-new',"loghub-thunderbird-new",
                  "loghub-spark-new", "loghub-proxifier-new", "loghub-openstack-new",
                  "loghub-openssh-new", "loghub-mac-new", "loghub-linux-new",
                  "loghub-hpc-new", "loghub-healthapp-new", "loghub-hdfsv3-new",
                  "loghub-hdfs-new", "loghub-hadoop-new", "loghub-bgl-new",
                  "loghub-apache-new", "loghub-android-new"]
    index_list = ["loghub-hdfsv3-new",
                  "loghub-hdfs-new", "loghub-hadoop-new", "loghub-bgl-new",
                  "loghub-apache-new", "loghub-android-new"]
    for index in index_list:
        source_index = index  
        target_index = index  

        docs  = export_data(source_client, source_index)
        
        mapping = get_source_index_mapping_and_settings(source_client, source_index)
        
        create_target_index(target_client, target_index, mapping)
        import_data(target_client, target_index, docs)
        print(f"index {index} finished!!!")

def search_logs():
    client = OpenSearch(
        hosts=[{'host': 'localhost', 
                'port': 9200}],  
        http_compress=True
    )
    query = {
    "_source": ["message"],  
    "size": 2000, 
    "query": {
        "bool": {
            "must_not": {
                "match_phrase": {
                    "response": "200"  
                }
            }
        }
        }
    }
    logs = search_index(client, "opensearch_dashboards_sample_data_logs", query)
    with open('response_logs.json', 'w') as f:
        json.dump(logs, f)


if __name__ == "__main__":
    transport_loghub_index()