from .base import AttackerBase
from dataclasses import dataclass, field
from gec_metrics import get_metric
from semsis.encoder import SentenceEncoder
from semsis.kvstore import KVStore
from semsis.retriever import RetrieverFaissCPU, Metric
import math
import numpy as np
from pathlib import Path
import torch
from tqdm import tqdm
import json
import pprint

class AttackerForIMPARA(AttackerBase):
    @dataclass
    class Config(AttackerBase.Config):
        corpus: list[str] = None
        model: str =  'google-bert/bert-base-cased'
        representation: str = 'avg'
        index_dir: str = 'exp-datasets/index'
        k: int = 256

    def __init__(self, config=None) -> None:
        super().__init__(config)
        Path(self.config.index_dir).mkdir(exist_ok=True, parents=True)
        self.impara = get_metric('impara')()
        self.encoder = SentenceEncoder.build(
            self.config.model,
            self.config.representation
        )
        if torch.cuda.is_available():
            self.encoder.cuda()
        self.index_dir = Path(self.config.index_dir)
        self.index_dir.mkdir(exist_ok=True, parents=True)
        KVSTORE_PATH = self.index_dir / 'kv.bin'
        INDEX_PATH = self.index_dir / 'index.bin'
        INDEX_CONFIG_PATH = self.index_dir / 'config.yaml'
        if INDEX_PATH.exists():
            # If the index exists, load this
            self.retriver = self.load_index(
                INDEX_PATH, INDEX_CONFIG_PATH
            )
        else:
            # Otherwise, create the index.
            # This takes a little long time depending on the data size.
            self.retriver = self.build_index(
                self.encoder, self.config.corpus,
                KVSTORE_PATH, INDEX_PATH, INDEX_CONFIG_PATH,
            )
        self.save_data = []

    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.save_data, f, indent=2)

    def build_index(
        self,
        encoder,
        text,
        kv_path,
        index_path,
        config_path
    ):
        print('Make KVStore...')
        
        BATCH_SIZE = 64
        TEXT = text
        dim = encoder.get_embed_dim()
        num_sentences = len(TEXT)
        # The retrieval process is entirely dependent on the Semsis library.
        # https://github.com/de9uch1/semsis
        with KVStore.open(kv_path, mode="w") as kvstore:
            # Initialize the kvstore.
            kvstore.new(dim)
            for i in range(math.ceil(num_sentences / BATCH_SIZE)):
                b, e = i * BATCH_SIZE, min((i + 1) * BATCH_SIZE, num_sentences)
                sentence_vectors = encoder.encode(TEXT[b:e]).cpu().numpy()
                kvstore.add(sentence_vectors)
        
        print('Build index...')
        with KVStore.open(kv_path, mode="r") as kvstore:
            retriever = RetrieverFaissCPU.build(RetrieverFaissCPU.Config(
                dim,
                metric=Metric.cos,
                hnsw_nlinks=32
            ))
            retriever.train(kvstore.key[:])
            retriever.add(kvstore.key[:], kvstore.value[:])
        retriever.save(index_path, config_path)
        print('Index was saved: ', index_path, config_path)
        return retriever
    
    def load_index(self, index_path, config_path):
        retriever = RetrieverFaissCPU.load(index_path, config_path)
        return retriever        
    
    def correct(self, sources: list[str]) -> list[str]:
        '''Correct source sentences.

        Args:
            sources (list[str]): Source sentences.

        Returns:
            list[str]: (Hacked) corrected sentences.
        '''
        hyps = []
        num_srcs = len(sources)
        batch_size = self.impara.config.batch_size
        search_results = []
        for batch_s in tqdm(range(0, num_srcs, batch_size)):
            batch = sources[batch_s: batch_s + batch_size]
            query_vectors = self.encoder.encode(batch).cpu().numpy()
            distance, indices = self.retriver.search(query_vectors, k=self.config.k)
            assert indices.shape == (len(batch), self.config.k)
            for example_id in range(len(indices)):
                idxs = indices[example_id]
                dis = distance[example_id]
                hyp_candidates = [
                    self.config.corpus[i] for knn_id, i in enumerate(idxs)
                    if dis[knn_id] > self.impara.config.threshold
                ]
                if hyp_candidates == []:
                    # If there is no appropriate candidates, simply return the source.
                    # The source can always pass the similarity estimator threshold.
                    hyps.append(batch[example_id])
                    continue
                scores = self.impara.score_sentence(
                    [batch[example_id]] * len(hyp_candidates),
                    hyp_candidates
                )
                best_hyp = sorted(
                    list(zip(hyp_candidates, scores, strict=True)),
                    key=lambda x: x[1]
                )[-1][0]  # [-1] is the max index of the scores, [0] refers to hyp_candidate
                hyps.append(best_hyp)

                best_idx = hyp_candidates.index(best_hyp)
                save_elem = {
                    'src': batch[example_id],
                    'hyp': best_hyp,
                    'distance': float(dis[best_idx]),
                    'indices': int(idxs[best_idx]),
                    'threshold-ratio': float(sum(d > 0.9 for d in dis) / len(dis)),
                    'k': len(dis)
                }
                self.save_data.append(save_elem)
        return hyps