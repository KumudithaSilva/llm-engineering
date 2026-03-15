#  🧪 Retrival Augmentation Evaluation Metrics

1. Curate a Test Set
    - Example `question set with right context` identified and reference answers provided.
    - Create a dataset with: `1) Question`, `2) Ground-truth document/chunk IDs`, `3) Expected answer`. Run retrieval and compare retrieved results with the ground truth.

2. MRR (Mean Reciprocal Rank)
    - It measures how `high the first relevant document` appears in the retrieval ranking.

3. NDCG (Normalized Discounted Cumulative Gain)
    - It measures `ranking quality considering multiple relevant documents`.
    - It used when there are `multiple relevant documents`.

4. Recall@K
    - It measures `how many of the relevant documents were retrieved` within the top K results.
    - This used when we want to `ensure the system does not miss useful context`.

5. Precision@K
    - It measures how many `retrieved documents in the top K are actually relevant`.
    - It ensures the retrieval system returns `less noise and more useful chunks`.

<br>

```
Example

1. Query: "What is Retrieval Augmented Generation?"

 > Retrieved top-3 chunks:

Chunk A (Relevant)
Chunk B (Not relevant)
Chunk C (Relevant)

======================================================================

1. Precision@3 = 2 / 3 = 0.67

======================================================================

2. Recall@3 = 2 / 2 = 1

======================================================================

3. MRR = 1 / 1 = 1 (first relevant result at rank 1)

======================================================================

4. NDCG (Normalized Discounted Cumulative Gain)

Compute DCG (Discounted Cumulative Gain)

| Rank | relᵢ | Calculation | Value |
| ---- | ---- | ----------- | ----- |
| 1    | 1    | 1 / log₂(2) | 1     |
| 2    | 0    | 0 / log₂(3) | 0     |
| 3    | 1    | 1 / log₂(4) | 0.5   |

DCG = 1 + 0 + 0.5 = 1.5


Compute IDCG (Ideal DCG)

- This is the best possible ranking that could be retrieved.

| Rank | relᵢ | Calculation | Value |
| ---- | ---- | ----------- | ----- |
| 1    | 1    | 1 / log₂(2) | 1     |
| 2    | 1    | 1 / log₂(3) | 0.63  |
| 3    | 0    | 0 / log₂(4) | 0     |

IDCG = 1 + 0.63 + 0 = 1.63


Compute NDCG

NDCG = DCG / IDCG
NDCG = 1.5 / 1.63
0.92


======================================================================
````

