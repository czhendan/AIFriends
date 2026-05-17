# RAG 检索评估报告
**生成时间**: 2026-05-16 21:18:55
**测试查询数**: 72

---

## 整体指标
| Method | Recall@3 | Recall@5 | Recall@10 | Hit Rate@3 | Hit Rate@5 | Hit Rate@10 | MRR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Vector-only | 0.9722 | 0.9861 | 0.9861 | 0.9722 | 0.9861 | 0.9861 | 0.8137 |
| BM25-only | 0.8472 | 0.9306 | 0.9444 | 0.8472 | 0.9306 | 0.9444 | 0.7677 |
| Hybrid(RRF) | 0.9306 | 0.9722 | 0.9861 | 0.9306 | 0.9722 | 0.9861 | 0.8344 |

---

## 逐查询详情
### q000: 阿里云百炼是什么平台？
- **相关文档**: chunk_0
- **Vector-only (k=10)**: ✅ 命中: ['chunk_0'] | 检索: chunk_0, chunk_17, chunk_8, chunk_15, chunk_16
- **BM25-only (k=10)**: ✅ 命中: ['chunk_0'] | 检索: chunk_0, chunk_17, chunk_8, chunk_18, chunk_3
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_0'] | 检索: chunk_0, chunk_17, chunk_8, chunk_15, chunk_18

### q001: 它提供哪些功能，适合开发者和业务人员用吗？
- **相关文档**: chunk_0
- **Vector-only (k=10)**: ✅ 命中: ['chunk_0'] | 检索: chunk_7, chunk_0, chunk_6, chunk_11, chunk_18
- **BM25-only (k=10)**: ✅ 命中: ['chunk_0'] | 检索: chunk_0, chunk_17, chunk_8, chunk_16, chunk_12
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_0'] | 检索: chunk_0, chunk_7, chunk_11, chunk_10, chunk_8

### q002: 我能在上面创建智能体和知识库问答应用吗？
- **相关文档**: chunk_0
- **Vector-only (k=10)**: ✅ 命中: ['chunk_0'] | 检索: chunk_0, chunk_11, chunk_6, chunk_22, chunk_10
- **BM25-only (k=10)**: ✅ 命中: ['chunk_0'] | 检索: chunk_0, chunk_10, chunk_16, chunk_11, chunk_19
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_0'] | 检索: chunk_0, chunk_11, chunk_10, chunk_16, chunk_22

### q003: 怎么用Python调用阿里云百炼的API？
- **相关文档**: chunk_1
- **Vector-only (k=10)**: ✅ 命中: ['chunk_1'] | 检索: chunk_1, chunk_0, chunk_8, chunk_14, chunk_17
- **BM25-only (k=10)**: ✅ 命中: ['chunk_1'] | 检索: chunk_1, chunk_16, chunk_12, chunk_19, chunk_17
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_1'] | 检索: chunk_1, chunk_16, chunk_0, chunk_17, chunk_12

### q004: 我想把原来用OpenAI的代码改成阿里云百炼的，需要改哪些地方？
- **相关文档**: chunk_1
- **Vector-only (k=10)**: ✅ 命中: ['chunk_1'] | 检索: chunk_1, chunk_0, chunk_8, chunk_17, chunk_16
- **BM25-only (k=10)**: ✅ 命中: ['chunk_1'] | 检索: chunk_16, chunk_17, chunk_1, chunk_0, chunk_12
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_1'] | 检索: chunk_1, chunk_16, chunk_0, chunk_17, chunk_8

### q005: 阿里云百炼在不同地域的base_url分别是什么？
- **相关文档**: chunk_1
- **Vector-only (k=10)**: ✅ 命中: ['chunk_1'] | 检索: chunk_17, chunk_0, chunk_1, chunk_18, chunk_4
- **BM25-only (k=10)**: ✅ 命中: ['chunk_1'] | 检索: chunk_17, chunk_3, chunk_4, chunk_2, chunk_1
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_1'] | 检索: chunk_17, chunk_1, chunk_4, chunk_3, chunk_18

### q006: 怎么用Python调用通义千问的qwen3.6-plus模型？
- **相关文档**: chunk_2
- **Vector-only (k=10)**: ✅ 命中: ['chunk_2'] | 检索: chunk_2, chunk_8, chunk_3, chunk_21, chunk_4
- **BM25-only (k=10)**: ✅ 命中: ['chunk_2'] | 检索: chunk_8, chunk_2, chunk_3, chunk_4, chunk_16
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_2'] | 检索: chunk_2, chunk_8, chunk_3, chunk_4, chunk_16

### q007: Node.js调用通义千问时base_url应该怎么设置？
- **相关文档**: chunk_2
- **Vector-only (k=10)**: ✅ 命中: ['chunk_2'] | 检索: chunk_2, chunk_4, chunk_3, chunk_1, chunk_21
- **BM25-only (k=10)**: ✅ 命中: ['chunk_2'] | 检索: chunk_2, chunk_20, chunk_1, chunk_16, chunk_8
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_2'] | 检索: chunk_2, chunk_1, chunk_4, chunk_3, chunk_16

### q008: 不同地域的base_url有什么区别？
- **相关文档**: chunk_2
- **Vector-only (k=10)**: ✅ 命中: ['chunk_2'] | 检索: chunk_4, chunk_3, chunk_2, chunk_18, chunk_1
- **BM25-only (k=10)**: ✅ 命中: ['chunk_2'] | 检索: chunk_17, chunk_2, chunk_3, chunk_4, chunk_1
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_2'] | 检索: chunk_4, chunk_3, chunk_2, chunk_17, chunk_18

### q009: 这个代码里用的是哪个模型？
- **相关文档**: chunk_3
- **Vector-only (k=10)**: ❌ 命中: 无 | 检索: chunk_21, chunk_8, chunk_18, chunk_17, chunk_7
- **BM25-only (k=10)**: ✅ 命中: ['chunk_3'] | 检索: chunk_16, chunk_7, chunk_12, chunk_0, chunk_10
- **Hybrid(RRF) (k=10)**: ❌ 命中: 无 | 检索: chunk_16, chunk_7, chunk_1, chunk_17, chunk_21

### q010: 新加坡和北京的base URL有什么区别？
- **相关文档**: chunk_3
- **Vector-only (k=10)**: ✅ 命中: ['chunk_3'] | 检索: chunk_4, chunk_3, chunk_2, chunk_18, chunk_21
- **BM25-only (k=10)**: ✅ 命中: ['chunk_3'] | 检索: chunk_17, chunk_1, chunk_2, chunk_3, chunk_4
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_3'] | 检索: chunk_4, chunk_3, chunk_2, chunk_17, chunk_1

### q011: 这个代码示例中baseURL设置的是哪个地域？
- **相关文档**: chunk_3
- **Vector-only (k=10)**: ✅ 命中: ['chunk_3'] | 检索: chunk_4, chunk_3, chunk_2, chunk_18, chunk_1
- **BM25-only (k=10)**: ✅ 命中: ['chunk_3'] | 检索: chunk_3, chunk_4, chunk_2, chunk_23, chunk_1
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_3'] | 检索: chunk_4, chunk_3, chunk_2, chunk_1, chunk_23

### q012: 北京地域的Base URL是什么？
- **相关文档**: chunk_4
- **Vector-only (k=10)**: ✅ 命中: ['chunk_4'] | 检索: chunk_4, chunk_3, chunk_2, chunk_18, chunk_21
- **BM25-only (k=10)**: ✅ 命中: ['chunk_4'] | 检索: chunk_3, chunk_4, chunk_2, chunk_1, chunk_17
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_4'] | 检索: chunk_4, chunk_3, chunk_2, chunk_18, chunk_1

### q013: 新加坡地域的Base URL和北京的一样吗？
- **相关文档**: chunk_4
- **Vector-only (k=10)**: ✅ 命中: ['chunk_4'] | 检索: chunk_4, chunk_3, chunk_18, chunk_17, chunk_2
- **BM25-only (k=10)**: ✅ 命中: ['chunk_4'] | 检索: chunk_17, chunk_2, chunk_1, chunk_3, chunk_4
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_4'] | 检索: chunk_17, chunk_4, chunk_3, chunk_2, chunk_1

### q014: 调用API时，请求头里的Authorization该怎么设置？
- **相关文档**: chunk_4
- **Vector-only (k=10)**: ✅ 命中: ['chunk_4'] | 检索: chunk_1, chunk_18, chunk_4, chunk_16, chunk_22
- **BM25-only (k=10)**: ✅ 命中: ['chunk_4'] | 检索: chunk_14, chunk_20, chunk_16, chunk_4, chunk_21
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_4'] | 检索: chunk_4, chunk_16, chunk_1, chunk_22, chunk_21

### q015: 这个表格有多少列？
- **相关文档**: chunk_5
- **Vector-only (k=10)**: ✅ 命中: ['chunk_5'] | 检索: chunk_23, chunk_24, chunk_5, chunk_7, chunk_13
- **BM25-only (k=10)**: ❌ 命中: 无 | 检索: chunk_23, chunk_24, chunk_14, chunk_9, chunk_17
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_5'] | 检索: chunk_23, chunk_24, chunk_14, chunk_17, chunk_5

### q016: 这个表格有多少行数据？
- **相关文档**: chunk_5
- **Vector-only (k=10)**: ✅ 命中: ['chunk_5'] | 检索: chunk_23, chunk_24, chunk_5, chunk_16, chunk_14
- **BM25-only (k=10)**: ❌ 命中: 无 | 检索: chunk_17, chunk_23, chunk_24, chunk_9, chunk_16
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_5'] | 检索: chunk_23, chunk_24, chunk_17, chunk_16, chunk_5

### q017: 怎么快速搭建一个AI客服来回答客户问题？
- **相关文档**: chunk_6
- **Vector-only (k=10)**: ✅ 命中: ['chunk_6'] | 检索: chunk_6, chunk_0, chunk_8, chunk_18, chunk_22
- **BM25-only (k=10)**: ✅ 命中: ['chunk_6'] | 检索: chunk_6, chunk_0, chunk_10, chunk_15, chunk_8
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_6'] | 检索: chunk_6, chunk_0, chunk_8, chunk_21, chunk_10

### q018: 没有代码基础的人也能设计业务流程吗？
- **相关文档**: chunk_6
- **Vector-only (k=10)**: ✅ 命中: ['chunk_6'] | 检索: chunk_7, chunk_6, chunk_23, chunk_16, chunk_22
- **BM25-only (k=10)**: ✅ 命中: ['chunk_6'] | 检索: chunk_7, chunk_6, chunk_16, chunk_0, chunk_17
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_6'] | 检索: chunk_7, chunk_6, chunk_16, chunk_23, chunk_1

### q019: 你们那个可视化的流程编排工具具体是做什么的？
- **相关文档**: chunk_6
- **Vector-only (k=10)**: ✅ 命中: ['chunk_6'] | 检索: chunk_7, chunk_6, chunk_22, chunk_0, chunk_10
- **BM25-only (k=10)**: ✅ 命中: ['chunk_6'] | 检索: chunk_6, chunk_7, chunk_0, chunk_22, chunk_15
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_6'] | 检索: chunk_7, chunk_6, chunk_22, chunk_0, chunk_15

### q020: 可视化流程编排适合没有编程基础的人使用吗？
- **相关文档**: chunk_7
- **Vector-only (k=10)**: ✅ 命中: ['chunk_7'] | 检索: chunk_7, chunk_6, chunk_22, chunk_15, chunk_21
- **BM25-only (k=10)**: ✅ 命中: ['chunk_7'] | 检索: chunk_7, chunk_6, chunk_8, chunk_22, chunk_16
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_7'] | 检索: chunk_7, chunk_6, chunk_22, chunk_15, chunk_21

### q021: 我不懂代码，能不能用这个工具来定制模型？
- **相关文档**: chunk_7
- **Vector-only (k=10)**: ✅ 命中: ['chunk_7'] | 检索: chunk_7, chunk_21, chunk_6, chunk_8, chunk_18
- **BM25-only (k=10)**: ✅ 命中: ['chunk_7'] | 检索: chunk_7, chunk_16, chunk_6, chunk_17, chunk_1
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_7'] | 检索: chunk_7, chunk_6, chunk_16, chunk_18, chunk_0

### q022: 阿里云百炼平台上有哪些可以直接用的模型？
- **相关文档**: chunk_8
- **Vector-only (k=10)**: ✅ 命中: ['chunk_8'] | 检索: chunk_8, chunk_0, chunk_17, chunk_16, chunk_15
- **BM25-only (k=10)**: ✅ 命中: ['chunk_8'] | 检索: chunk_8, chunk_17, chunk_0, chunk_9, chunk_12
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_8'] | 检索: chunk_8, chunk_0, chunk_17, chunk_16, chunk_18

### q023: 千问Max、千问Plus和千问Flash这几个模型有什么区别？
- **相关文档**: chunk_8
- **Vector-only (k=10)**: ✅ 命中: ['chunk_8'] | 检索: chunk_8, chunk_3, chunk_2, chunk_21, chunk_4
- **BM25-only (k=10)**: ✅ 命中: ['chunk_8'] | 检索: chunk_8, chunk_17, chunk_9, chunk_16, chunk_22
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_8'] | 检索: chunk_8, chunk_3, chunk_2, chunk_16, chunk_9

### q024: 你们支持哪些多模态能力，比如图像生成或语音识别？
- **相关文档**: chunk_8
- **Vector-only (k=10)**: ✅ 命中: ['chunk_8'] | 检索: chunk_8, chunk_9, chunk_7, chunk_18, chunk_11
- **BM25-only (k=10)**: ✅ 命中: ['chunk_8'] | 检索: chunk_8, chunk_11, chunk_17, chunk_10, chunk_21
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_8'] | 检索: chunk_8, chunk_11, chunk_17, chunk_9, chunk_18

### q025: 你们有哪些细分领域的模型可以用？
- **相关文档**: chunk_9
- **Vector-only (k=10)**: ✅ 命中: ['chunk_9'] | 检索: chunk_9, chunk_8, chunk_18, chunk_17, chunk_21
- **BM25-only (k=10)**: ✅ 命中: ['chunk_9'] | 检索: chunk_9, chunk_17, chunk_0, chunk_12, chunk_11
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_9'] | 检索: chunk_9, chunk_17, chunk_0, chunk_8, chunk_16

### q026: 模型调优支持哪些训练方法？
- **相关文档**: chunk_9
- **Vector-only (k=10)**: ✅ 命中: ['chunk_9'] | 检索: chunk_9, chunk_7, chunk_18, chunk_10, chunk_20
- **BM25-only (k=10)**: ✅ 命中: ['chunk_9'] | 检索: chunk_9, chunk_10, chunk_17, chunk_11, chunk_18
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_9'] | 检索: chunk_9, chunk_10, chunk_18, chunk_11, chunk_14

### q027: 模型部署的计费方式有哪些？
- **相关文档**: chunk_9
- **Vector-only (k=10)**: ✅ 命中: ['chunk_9'] | 检索: chunk_18, chunk_9, chunk_20, chunk_19, chunk_12
- **BM25-only (k=10)**: ✅ 命中: ['chunk_9'] | 检索: chunk_9, chunk_17, chunk_19, chunk_12, chunk_11
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_9'] | 检索: chunk_9, chunk_19, chunk_12, chunk_10, chunk_8

### q028: 模型评测里有哪些评测方式可以用？
- **相关文档**: chunk_10
- **Vector-only (k=10)**: ✅ 命中: ['chunk_10'] | 检索: chunk_10, chunk_14, chunk_18, chunk_21, chunk_16
- **BM25-only (k=10)**: ✅ 命中: ['chunk_10'] | 检索: chunk_9, chunk_17, chunk_10, chunk_0, chunk_12
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_10'] | 检索: chunk_10, chunk_9, chunk_16, chunk_8, chunk_20

### q029: 我想快速创建一个智能体应用，应该用可视化还是高代码模式？
- **相关文档**: chunk_10
- **Vector-only (k=10)**: ✅ 命中: ['chunk_10'] | 检索: chunk_6, chunk_10, chunk_22, chunk_0, chunk_7
- **BM25-only (k=10)**: ✅ 命中: ['chunk_10'] | 检索: chunk_10, chunk_0, chunk_6, chunk_16, chunk_22
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_10'] | 检索: chunk_10, chunk_6, chunk_0, chunk_22, chunk_7

### q030: 高代码应用支持哪些运维能力？
- **相关文档**: chunk_10
- **Vector-only (k=10)**: ✅ 命中: ['chunk_10'] | 检索: chunk_10, chunk_6, chunk_11, chunk_7, chunk_0
- **BM25-only (k=10)**: ✅ 命中: ['chunk_10'] | 检索: chunk_10, chunk_11, chunk_0, chunk_8, chunk_9
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_10'] | 检索: chunk_10, chunk_11, chunk_0, chunk_6, chunk_7

### q031: 怎么把我的AI应用分享到钉钉或者微信公众号上？
- **相关文档**: chunk_11
- **Vector-only (k=10)**: ✅ 命中: ['chunk_11'] | 检索: chunk_11, chunk_6, chunk_22, chunk_0, chunk_7
- **BM25-only (k=10)**: ✅ 命中: ['chunk_11'] | 检索: chunk_11, chunk_16, chunk_17, chunk_0, chunk_8
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_11'] | 检索: chunk_11, chunk_16, chunk_0, chunk_6, chunk_22

### q032: 这个功能拓展里的知识库、插件和MCP是干什么用的？
- **相关文档**: chunk_11
- **Vector-only (k=10)**: ✅ 命中: ['chunk_11'] | 检索: chunk_11, chunk_7, chunk_6, chunk_22, chunk_23
- **BM25-only (k=10)**: ✅ 命中: ['chunk_11'] | 检索: chunk_11, chunk_0, chunk_12, chunk_20, chunk_17
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_11'] | 检索: chunk_11, chunk_7, chunk_0, chunk_8, chunk_18

### q033: 开通阿里云百炼需要付费吗？
- **相关文档**: chunk_12
- **Vector-only (k=10)**: ✅ 命中: ['chunk_12'] | 检索: chunk_12, chunk_18, chunk_0, chunk_17, chunk_19
- **BM25-only (k=10)**: ✅ 命中: ['chunk_12'] | 检索: chunk_12, chunk_17, chunk_16, chunk_8, chunk_18
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_12'] | 检索: chunk_12, chunk_17, chunk_18, chunk_0, chunk_16

### q034: 新用户有什么免费额度可以用？
- **相关文档**: chunk_12
- **Vector-only (k=10)**: ✅ 命中: ['chunk_12'] | 检索: chunk_12, chunk_20, chunk_18, chunk_13, chunk_15
- **BM25-only (k=10)**: ✅ 命中: ['chunk_12'] | 检索: chunk_12, chunk_20, chunk_17, chunk_0, chunk_6
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_12'] | 检索: chunk_12, chunk_20, chunk_15, chunk_16, chunk_21

### q035: 调用模型怎么扣费，账户余额不足怎么办？
- **相关文档**: chunk_12
- **Vector-only (k=10)**: ✅ 命中: ['chunk_12'] | 检索: chunk_18, chunk_20, chunk_12, chunk_14, chunk_19
- **BM25-only (k=10)**: ✅ 命中: ['chunk_12'] | 检索: chunk_12, chunk_18, chunk_21, chunk_22, chunk_14
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_12'] | 检索: chunk_18, chunk_12, chunk_21, chunk_14, chunk_19

### q036: 怎么查看我的消费明细？
- **相关文档**: chunk_13
- **Vector-only (k=10)**: ✅ 命中: ['chunk_13'] | 检索: chunk_13, chunk_14, chunk_20, chunk_18, chunk_15
- **BM25-only (k=10)**: ✅ 命中: ['chunk_13'] | 检索: chunk_13, chunk_20, chunk_16, chunk_17, chunk_14
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_13'] | 检索: chunk_13, chunk_20, chunk_14, chunk_15, chunk_12

### q037: 账单详情和成本分析的页面在哪里？
- **相关文档**: chunk_13
- **Vector-only (k=10)**: ✅ 命中: ['chunk_13'] | 检索: chunk_13, chunk_20, chunk_18, chunk_12, chunk_14
- **BM25-only (k=10)**: ✅ 命中: ['chunk_13'] | 检索: chunk_13, chunk_20, chunk_12, chunk_8, chunk_21
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_13'] | 检索: chunk_13, chunk_20, chunk_12, chunk_14, chunk_19

### q038: 我想查一下费用使用情况，应该去哪里看？
- **相关文档**: chunk_13
- **Vector-only (k=10)**: ✅ 命中: ['chunk_13'] | 检索: chunk_13, chunk_20, chunk_18, chunk_14, chunk_12
- **BM25-only (k=10)**: ❌ 命中: 无 | 检索: chunk_15, chunk_19, chunk_12, chunk_21, chunk_18
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_13'] | 检索: chunk_15, chunk_20, chunk_18, chunk_12, chunk_19

### q039: 模型调用完多久才能看到统计结果？
- **相关文档**: chunk_14
- **Vector-only (k=10)**: ✅ 命中: ['chunk_14'] | 检索: chunk_14, chunk_18, chunk_16, chunk_20, chunk_7
- **BM25-only (k=10)**: ✅ 命中: ['chunk_14'] | 检索: chunk_14, chunk_22, chunk_12, chunk_21, chunk_19
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_14'] | 检索: chunk_14, chunk_22, chunk_18, chunk_16, chunk_12

### q040: 怎么查看某个模型的调用量、Token消耗和成功率？
- **相关文档**: chunk_14
- **Vector-only (k=10)**: ✅ 命中: ['chunk_14'] | 检索: chunk_14, chunk_18, chunk_20, chunk_16, chunk_22
- **BM25-only (k=10)**: ✅ 命中: ['chunk_14'] | 检索: chunk_14, chunk_9, chunk_15, chunk_13, chunk_20
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_14'] | 检索: chunk_14, chunk_20, chunk_15, chunk_21, chunk_12

### q041: 在阿里云百炼控制台怎么找到模型监控页面？
- **相关文档**: chunk_14
- **Vector-only (k=10)**: ✅ 命中: ['chunk_14'] | 检索: chunk_14, chunk_15, chunk_0, chunk_17, chunk_16
- **BM25-only (k=10)**: ✅ 命中: ['chunk_14'] | 检索: chunk_14, chunk_15, chunk_19, chunk_21, chunk_20
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_14'] | 检索: chunk_14, chunk_15, chunk_19, chunk_17, chunk_20

### q042: 怎么查看我Coding Plan套餐的请求消耗情况？
- **相关文档**: chunk_15
- **Vector-only (k=10)**: ✅ 命中: ['chunk_15'] | 检索: chunk_15, chunk_13, chunk_14, chunk_20, chunk_21
- **BM25-only (k=10)**: ✅ 命中: ['chunk_15'] | 检索: chunk_15, chunk_21, chunk_16, chunk_14, chunk_17
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_15'] | 检索: chunk_15, chunk_21, chunk_14, chunk_13, chunk_20

### q043: Coding Plan是月付的吗，每个月有多少额度？
- **相关文档**: chunk_15
- **Vector-only (k=10)**: ✅ 命中: ['chunk_15'] | 检索: chunk_18, chunk_15, chunk_12, chunk_20, chunk_21
- **BM25-only (k=10)**: ✅ 命中: ['chunk_15'] | 检索: chunk_15, chunk_21, chunk_16, chunk_17, chunk_12
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_15'] | 检索: chunk_15, chunk_21, chunk_12, chunk_20, chunk_18

### q044: 在哪里可以在线体验阿里云百炼的大模型？
- **相关文档**: chunk_15
- **Vector-only (k=10)**: ✅ 命中: ['chunk_15'] | 检索: chunk_0, chunk_17, chunk_16, chunk_15, chunk_8
- **BM25-only (k=10)**: ✅ 命中: ['chunk_15'] | 检索: chunk_15, chunk_0, chunk_21, chunk_16, chunk_17
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_15'] | 检索: chunk_0, chunk_15, chunk_17, chunk_16, chunk_21

### q045: 怎么在阿里云百炼上体验模型？
- **相关文档**: chunk_16
- **Vector-only (k=10)**: ✅ 命中: ['chunk_16'] | 检索: chunk_16, chunk_0, chunk_15, chunk_17, chunk_8
- **BM25-only (k=10)**: ✅ 命中: ['chunk_16'] | 检索: chunk_8, chunk_15, chunk_21, chunk_12, chunk_16
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_16'] | 检索: chunk_15, chunk_16, chunk_8, chunk_0, chunk_17

### q046: 第一次调用千问API的步骤是什么？
- **相关文档**: chunk_16
- **Vector-only (k=10)**: ✅ 命中: ['chunk_16'] | 检索: chunk_22, chunk_16, chunk_18, chunk_1, chunk_21
- **BM25-only (k=10)**: ✅ 命中: ['chunk_16'] | 检索: chunk_8, chunk_22, chunk_16, chunk_3, chunk_4
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_16'] | 检索: chunk_22, chunk_16, chunk_8, chunk_3, chunk_2

### q047: 不用写代码能搭建一个问答应用吗？
- **相关文档**: chunk_16
- **Vector-only (k=10)**: ✅ 命中: ['chunk_16'] | 检索: chunk_16, chunk_6, chunk_22, chunk_0, chunk_10
- **BM25-only (k=10)**: ✅ 命中: ['chunk_16'] | 检索: chunk_16, chunk_0, chunk_6, chunk_7, chunk_10
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_16'] | 检索: chunk_16, chunk_6, chunk_0, chunk_10, chunk_22

### q048: 阿里云百炼会不会拿我的数据去训练模型？
- **相关文档**: chunk_16
- **Vector-only (k=10)**: ✅ 命中: ['chunk_16'] | 检索: chunk_17, chunk_16, chunk_0, chunk_14, chunk_12
- **BM25-only (k=10)**: ✅ 命中: ['chunk_16'] | 检索: chunk_17, chunk_16, chunk_12, chunk_0, chunk_1
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_16'] | 检索: chunk_17, chunk_16, chunk_0, chunk_12, chunk_14

### q049: 我的数据在阿里云百炼上安全吗？你们会不会拿我的数据去训练模型？
- **相关文档**: chunk_17
- **Vector-only (k=10)**: ✅ 命中: ['chunk_17'] | 检索: chunk_17, chunk_16, chunk_0, chunk_18, chunk_14
- **BM25-only (k=10)**: ✅ 命中: ['chunk_17'] | 检索: chunk_17, chunk_16, chunk_12, chunk_8, chunk_15
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_17'] | 检索: chunk_17, chunk_16, chunk_0, chunk_12, chunk_8

### q050: 阿里云百炼在中国和美国都有服务吗？不同地域的模型服务有啥区别？
- **相关文档**: chunk_17
- **Vector-only (k=10)**: ✅ 命中: ['chunk_17'] | 检索: chunk_17, chunk_8, chunk_0, chunk_18, chunk_1
- **BM25-only (k=10)**: ✅ 命中: ['chunk_17'] | 检索: chunk_17, chunk_1, chunk_20, chunk_18, chunk_9
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_17'] | 检索: chunk_17, chunk_1, chunk_18, chunk_8, chunk_16

### q051: 为什么我调用API延迟很高？是不是选个近的地域就能解决？
- **相关文档**: chunk_18
- **Vector-only (k=10)**: ✅ 命中: ['chunk_18'] | 检索: chunk_18, chunk_4, chunk_3, chunk_1, chunk_17
- **BM25-only (k=10)**: ✅ 命中: ['chunk_18'] | 检索: chunk_16, chunk_18, chunk_17, chunk_9, chunk_10
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_18'] | 检索: chunk_18, chunk_17, chunk_16, chunk_1, chunk_21

### q052: 不同地域的API Key能通用吗？
- **相关文档**: chunk_18
- **Vector-only (k=10)**: ✅ 命中: ['chunk_18'] | 检索: chunk_4, chunk_18, chunk_3, chunk_1, chunk_17
- **BM25-only (k=10)**: ✅ 命中: ['chunk_18'] | 检索: chunk_2, chunk_18, chunk_3, chunk_4, chunk_1
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_18'] | 检索: chunk_18, chunk_4, chunk_3, chunk_2, chunk_1

### q053: 我不想被自动扣费，有什么办法可以避免？
- **相关文档**: chunk_18
- **Vector-only (k=10)**: ✅ 命中: ['chunk_18'] | 检索: chunk_18, chunk_20, chunk_12, chunk_13, chunk_19
- **BM25-only (k=10)**: ✅ 命中: ['chunk_18'] | 检索: chunk_18, chunk_17, chunk_12, chunk_20, chunk_16
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_18'] | 检索: chunk_18, chunk_20, chunk_12, chunk_6, chunk_21

### q054: 怎么彻底关闭阿里云百炼，防止继续扣费？
- **相关文档**: chunk_19
- **Vector-only (k=10)**: ✅ 命中: ['chunk_19'] | 检索: chunk_19, chunk_18, chunk_12, chunk_17, chunk_0
- **BM25-only (k=10)**: ✅ 命中: ['chunk_19'] | 检索: chunk_18, chunk_12, chunk_19, chunk_21, chunk_9
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_19'] | 检索: chunk_18, chunk_19, chunk_12, chunk_17, chunk_0

### q055: 删除API Key之后还需要做什么才能确保不再产生费用？
- **相关文档**: chunk_19
- **Vector-only (k=10)**: ✅ 命中: ['chunk_19'] | 检索: chunk_19, chunk_18, chunk_20, chunk_12, chunk_1
- **BM25-only (k=10)**: ✅ 命中: ['chunk_19'] | 检索: chunk_19, chunk_18, chunk_12, chunk_17, chunk_21
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_19'] | 检索: chunk_19, chunk_18, chunk_12, chunk_1, chunk_2

### q056: 如果我有定时任务在调用模型，该怎么停止它们？
- **相关文档**: chunk_19
- **Vector-only (k=10)**: ✅ 命中: ['chunk_19'] | 检索: chunk_19, chunk_20, chunk_18, chunk_14, chunk_22
- **BM25-only (k=10)**: ✅ 命中: ['chunk_19'] | 检索: chunk_19, chunk_17, chunk_14, chunk_8, chunk_15
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_19'] | 检索: chunk_19, chunk_14, chunk_20, chunk_8, chunk_16

### q057: 开启免费额度用完即停的开关后，是不是只要免费额度没用完就不会扣钱？
- **相关文档**: chunk_20
- **Vector-only (k=10)**: ✅ 命中: ['chunk_20'] | 检索: chunk_20, chunk_18, chunk_12, chunk_13, chunk_19
- **BM25-only (k=10)**: ✅ 命中: ['chunk_20'] | 检索: chunk_20, chunk_12, chunk_18, chunk_14, chunk_10
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_20'] | 检索: chunk_20, chunk_18, chunk_12, chunk_14, chunk_15

### q058: 我开通了免费额度，但担心不小心用超了，怎么设置预警或者监控来提醒我？
- **相关文档**: chunk_20
- **Vector-only (k=10)**: ✅ 命中: ['chunk_20'] | 检索: chunk_20, chunk_18, chunk_13, chunk_12, chunk_14
- **BM25-only (k=10)**: ✅ 命中: ['chunk_20'] | 检索: chunk_20, chunk_12, chunk_14, chunk_0, chunk_16
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_20'] | 检索: chunk_20, chunk_12, chunk_14, chunk_18, chunk_16

### q059: 免费额度用完后，如果没开那个“用完即停”开关，是不是就会自动转成付费继续使用？
- **相关文档**: chunk_20
- **Vector-only (k=10)**: ✅ 命中: ['chunk_20'] | 检索: chunk_20, chunk_18, chunk_12, chunk_19, chunk_13
- **BM25-only (k=10)**: ✅ 命中: ['chunk_20'] | 检索: chunk_12, chunk_20, chunk_18, chunk_15, chunk_21
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_20'] | 检索: chunk_20, chunk_12, chunk_18, chunk_15, chunk_21

### q060: Coding Plan是固定月费吗？会不会有按量扣费的风险？
- **相关文档**: chunk_21
- **Vector-only (k=10)**: ✅ 命中: ['chunk_21'] | 检索: chunk_18, chunk_15, chunk_21, chunk_20, chunk_12
- **BM25-only (k=10)**: ✅ 命中: ['chunk_21'] | 检索: chunk_21, chunk_15, chunk_12, chunk_16, chunk_17
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_21'] | 检索: chunk_21, chunk_15, chunk_18, chunk_12, chunk_20

### q061: 使用Coding Plan时，必须用哪个Base URL和API Key才能避免按量付费？
- **相关文档**: chunk_21
- **Vector-only (k=10)**: ✅ 命中: ['chunk_21'] | 检索: chunk_21, chunk_18, chunk_15, chunk_4, chunk_3
- **BM25-only (k=10)**: ✅ 命中: ['chunk_21'] | 检索: chunk_21, chunk_18, chunk_15, chunk_20, chunk_2
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_21'] | 检索: chunk_21, chunk_18, chunk_15, chunk_20, chunk_2

### q062: 怎么在线体验Qwen3系列模型或DeepSeek？DeepSeek只支持哪个地域？
- **相关文档**: chunk_21
- **Vector-only (k=10)**: ✅ 命中: ['chunk_21'] | 检索: chunk_21, chunk_3, chunk_8, chunk_2, chunk_4
- **BM25-only (k=10)**: ✅ 命中: ['chunk_21'] | 检索: chunk_21, chunk_8, chunk_15, chunk_1, chunk_11
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_21'] | 检索: chunk_21, chunk_8, chunk_3, chunk_2, chunk_1

### q063: 怎么通过API调用千问模型？
- **相关文档**: chunk_22
- **Vector-only (k=10)**: ✅ 命中: ['chunk_22'] | 检索: chunk_22, chunk_16, chunk_1, chunk_8, chunk_21
- **BM25-only (k=10)**: ✅ 命中: ['chunk_22'] | 检索: chunk_22, chunk_16, chunk_8, chunk_11, chunk_12
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_22'] | 检索: chunk_22, chunk_16, chunk_8, chunk_1, chunk_21

### q064: 有没有办法用Claude Code这样的开发工具来调用模型？
- **相关文档**: chunk_22
- **Vector-only (k=10)**: ✅ 命中: ['chunk_22'] | 检索: chunk_22, chunk_21, chunk_1, chunk_15, chunk_18
- **BM25-only (k=10)**: ✅ 命中: ['chunk_22'] | 检索: chunk_22, chunk_12, chunk_16, chunk_23, chunk_24
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_22'] | 检索: chunk_22, chunk_16, chunk_10, chunk_21, chunk_12

### q065: 我想用可视化界面搭建大模型应用，该怎么做？
- **相关文档**: chunk_22
- **Vector-only (k=10)**: ✅ 命中: ['chunk_22'] | 检索: chunk_6, chunk_22, chunk_7, chunk_0, chunk_10
- **BM25-only (k=10)**: ✅ 命中: ['chunk_22'] | 检索: chunk_16, chunk_22, chunk_17, chunk_0, chunk_10
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_22'] | 检索: chunk_22, chunk_16, chunk_6, chunk_0, chunk_10

### q066: 如何让表格显示成类似钉钉文档的分栏卡片？
- **相关文档**: chunk_23
- **Vector-only (k=10)**: ✅ 命中: ['chunk_23'] | 检索: chunk_23, chunk_24, chunk_7, chunk_11, chunk_6
- **BM25-only (k=10)**: ✅ 命中: ['chunk_23'] | 检索: chunk_23, chunk_24, chunk_11, chunk_6, chunk_18
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_23'] | 检索: chunk_23, chunk_24, chunk_11, chunk_6, chunk_7

### q067: 怎么调整表格里代码块的字体大小让它更紧凑？
- **相关文档**: chunk_23
- **Vector-only (k=10)**: ✅ 命中: ['chunk_23'] | 检索: chunk_24, chunk_23, chunk_7, chunk_1, chunk_5
- **BM25-only (k=10)**: ✅ 命中: ['chunk_23'] | 检索: chunk_23, chunk_0, chunk_1, chunk_7, chunk_6
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_23'] | 检索: chunk_23, chunk_24, chunk_7, chunk_1, chunk_6

### q068: 表格中代码块的间距怎么缩小？
- **相关文档**: chunk_23
- **Vector-only (k=10)**: ✅ 命中: ['chunk_23'] | 检索: chunk_24, chunk_23, chunk_7, chunk_5, chunk_1
- **BM25-only (k=10)**: ✅ 命中: ['chunk_23'] | 检索: chunk_23, chunk_24, chunk_7, chunk_1, chunk_10
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_23'] | 检索: chunk_24, chunk_23, chunk_7, chunk_1, chunk_5

### q069: 怎么让代码块里的文字变小一点？
- **相关文档**: chunk_24
- **Vector-only (k=10)**: ✅ 命中: ['chunk_24'] | 检索: chunk_24, chunk_23, chunk_7, chunk_1, chunk_2
- **BM25-only (k=10)**: ❌ 命中: 无 | 检索: chunk_23, chunk_7, chunk_6, chunk_0, chunk_1
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_24'] | 检索: chunk_23, chunk_7, chunk_1, chunk_6, chunk_24

### q070: 表格里引用块的上下间距太宽了，怎么调紧凑些？
- **相关文档**: chunk_24
- **Vector-only (k=10)**: ✅ 命中: ['chunk_24'] | 检索: chunk_24, chunk_23, chunk_5, chunk_7, chunk_18
- **BM25-only (k=10)**: ✅ 命中: ['chunk_24'] | 检索: chunk_24, chunk_23, chunk_0, chunk_11, chunk_7
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_24'] | 检索: chunk_24, chunk_23, chunk_7, chunk_11, chunk_6

### q071: 我想让代码块字体变成12px，该怎么做？
- **相关文档**: chunk_24
- **Vector-only (k=10)**: ✅ 命中: ['chunk_24'] | 检索: chunk_24, chunk_23, chunk_1, chunk_7, chunk_2
- **BM25-only (k=10)**: ✅ 命中: ['chunk_24'] | 检索: chunk_23, chunk_16, chunk_7, chunk_6, chunk_24
- **Hybrid(RRF) (k=10)**: ✅ 命中: ['chunk_24'] | 检索: chunk_23, chunk_24, chunk_7, chunk_1, chunk_6

