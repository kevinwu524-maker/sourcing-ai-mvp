# Sourcing AI MVP V6

V6 重点：更细颗粒度的 benchmark-based grading。

相比 V5，V6 把很多“好 / 一般 / 差”的选项改成更可执行的业务阈值，例如：

- 月 GMV、月订单量
- 粉丝数 / 私域名单规模 / 互动率
- 广告预算区间
- 毛利率区间
- MOQ 与客户预算倍率
- 响应时间和决策权
- SKU、素材、收款、履约准备度
- 可触达达人/分销伙伴数量

## 运行方法

```bash
cd ~/Downloads
unzip sourcing_ai_mvp_v6.zip
cd sourcing_ai_mvp_v6
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

打开：

```text
http://localhost:8501
```

## 使用建议

1. 先把 interview/call notes 粘到 Step 0，系统给自动预评分和路线建议。
2. 再用 Step 1-3 人工复核。
3. 没有证据时不要选最高档。
4. 粉丝数不能单独算高分，要看能不能触达、是否互动、是否能转化。
5. 介于两个档位之间，默认选低一档，把缺口放进 follow-up questions。
