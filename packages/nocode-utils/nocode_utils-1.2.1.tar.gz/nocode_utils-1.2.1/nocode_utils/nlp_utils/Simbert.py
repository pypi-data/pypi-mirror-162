# encoding: utf-8
"""
-------------------------------------------------
@author: haohe
@email: haohe@nocode.com
@software: PyCharm
@file: Simbert.py
@time: 2022/8/9 10:43
@description:
-------------------------------------------------
"""
import numpy as np
from bert4keras.backend import keras
from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer
from bert4keras.snippets import sequence_padding, AutoRegressiveDecoder

class SimBERT:
    class SynonymsGenerator(AutoRegressiveDecoder):
        """seq2seq解码器
        """

        def __init__(self, simbert, start_id, end_id, maxlen):
            super().__init__(start_id, end_id, maxlen)
            self.simbert = simbert

        @AutoRegressiveDecoder.set_rtype('probas')
        def predict(self, inputs, output_ids, step):
            token_ids, segment_ids = inputs
            token_ids = np.concatenate([token_ids, output_ids], 1)
            segment_ids = np.concatenate(
                [segment_ids, np.ones_like(output_ids)], 1)
            return self.simbert.seq2seq.predict([token_ids, segment_ids])[:, -1]

        def generate(self, text, n=1, topk=5):
            token_ids, segment_ids = self.simbert.tokenizer.encode(text, max_length=32)
            output_ids = self.random_sample([token_ids, segment_ids], n, topk)  # 基于随机采样
            return [self.simbert.tokenizer.decode(ids) for ids in output_ids]

    def __init__(self, model_path):
        maxlen = 32
        config_path = model_path + '/bert_config.json'
        checkpoint_path = model_path + '/bert_model.ckpt'
        dict_path = model_path + '/vocab.txt'
        self.tokenizer = Tokenizer(dict_path, do_lower_case=True)  # 建立分词器

        # 建立加载模型
        self.bert = build_transformer_model(
            config_path,
            checkpoint_path,
            with_pool='linear',
            application='unilm',
            return_keras_model=False,
        )

        self.encoder = keras.models.Model(self.bert.model.inputs, self.bert.model.outputs[0])
        self.seq2seq = keras.models.Model(self.bert.model.inputs, self.bert.model.outputs[1])

        self.synonyms_generator = self.SynonymsGenerator(self,
                                                         start_id=None,
                                                         end_id=self.tokenizer._token_end_id,
                                                         maxlen=maxlen)

    def gen_synonyms(self, text, n=100, k=20):
        """
        simbert 生成相似句子
        模型下载地址：https://github.com/ZhuiyiTechnology/pretrained-models
        选择 SimBERT-Tiny, SimBERT-Small, SimBERT-Base 其中之一
        源码地址：https://github.com/ZhuiyiTechnology/simbert
        需要 pip install tensorflow==1.14 keras==2.3.1 bert4keras==0.7.7
        :param text:
        :return:
        """

        r = self.synonyms_generator.generate(text, n)
        r = [i for i in set(r) if i != text]
        r = [text] + r
        X, S = [], []
        for t in r:
            x, s = self.tokenizer.encode(t)
            X.append(x)
            S.append(s)
        X = sequence_padding(X)
        S = sequence_padding(S)
        Z = self.encoder.predict([X, S])
        Z /= (Z ** 2).sum(axis=1, keepdims=True) ** 0.5
        argsort = np.dot(Z[1:], -Z[0]).argsort()
        return [r[i + 1] for i in argsort[:k]]
