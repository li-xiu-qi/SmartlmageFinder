
from sentence_transformers import SentenceTransformer


model = SentenceTransformer(
    r"C:\Users\k\Desktop\BaiduSyncdisk\baidu_sync_documents\hf_models\jina-clip-v2",
    trust_remote_code=True,
)

# clip 模型似乎无法通过这个方法获取维度
vector_dim = model.get_sentence_embedding_dimension()

print(vector_dim)