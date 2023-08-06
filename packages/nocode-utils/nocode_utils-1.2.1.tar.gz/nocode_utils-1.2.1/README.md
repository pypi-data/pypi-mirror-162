## 封装常用函数和类

不会预先安装所有依赖包，需要时推荐安装版本：
- DBUtils==1.3
- pymysql==1.0.2
- psycopg2-binary==2.9.1
- requests==2.26.0
- nlpcda==2.5.8

### 结构
- nocode_utils
    - http_utils
      - def http_post
      - def http_get
    - database_utils
        - class DBProcessor
    - threading_utils
         - class Threads
    - nlp_utils
      - data_augmentation
        - def ramdom_word
        - def similar_word
        - def homophone
        - def char_position_exchange
        - def equivalent_char
        - def SimGenerator
      - data_preprocess
        - def is_all_chinese
        - def is_contains_chinese
        - def is_contains_english
        - def only_keep_chinese
        - def get_sentence_num
      - common
        - def get_embedding
        - def get_similarity
        - def get_entity