import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Sourcing AI Scoring Tool V8", page_icon="🧭", layout="wide")



# -----------------------------
# V8 sample cases for onboarding and calibration
# -----------------------------
SAMPLE_CASES = {
    "Case 1｜Shopify Seller：有销量，缺 sourcing + affiliate 增长": {
        "expected_route": "Sourcing Support + MyyBiz CPS / Store",
        "expected_level": "B+/A-，但需要补证据",
        "transcript": """Client Name: HomeGlow Studio\nProduct Category: Home decor / LED mirror / room accessories\nInterview Date: Sample\n\nBD: Thanks for taking the time. Could you tell me a bit about what you're selling now and where you're selling it?\nClient: We sell home decor items, mostly LED mirrors and small room accessories. We currently sell through Shopify and TikTok Shop. Shopify is doing around $8,000 to $12,000 monthly GMV, TikTok Shop is smaller, maybe 40 to 60 orders a month.\nBD: What is your biggest challenge right now?\nClient: Sourcing is the biggest one. The price we get from our current supplier is not stable, and sometimes the quality is inconsistent. We also want to test creator promotion, but we are not sure what commission rate makes sense.\nBD: For the product you're looking for, is it existing product or custom?\nClient: Mostly existing product, but we want custom packaging and maybe our logo on the box. Target retail price is around $59 to $79. Ideally landed cost should be under $28. For first order, we can accept 300 units if the sample is good.\nBD: Are you running paid ads or influencer campaigns?\nClient: We spend around $500 to $1,000 per month on TikTok ads, but creator content performs better than ads. We can offer 12% to 18% commission if the margin works.\nBD: Do you have product images or videos ready?\nClient: Yes, we have Shopify product pages, photos, and some short videos. We can share the store link and sales screenshots after the call.\nBD: For growth, are you mainly looking to sell more through your store or through affiliates?\nClient: Both. We want to keep our own store, but also let creators sell with trackable links.\n""",
        "training_note": "这个案例不应该只推 MyyBiz demo。第一步是 sourcing 验证：目标价、MOQ、样品、包装。验证后再推 CPS/affiliate。"
    },
    "Case 2｜Creator：强内容能力，无供应链，适合 Co-Creation": {
        "expected_route": "Co-Creation",
        "expected_level": "A-/B+，取决于受众和转化证据",
        "transcript": """Client Name: Maya Lee\nProduct Category: Streetwear / lifestyle accessories\nInterview Date: Sample\n\nBD: Could you tell me a bit about your content and audience?\nClient: I create streetwear and lifestyle content. I have about 180,000 followers on TikTok and 62,000 on Instagram. My audience is mostly women 18 to 28 in the U.S. I post outfit videos, thrift flips, and product styling. My average TikTok video gets around 20,000 to 50,000 views, and some videos go over 300,000.\nBD: Have you sold your own products before?\nClient: Not my own product. I have done affiliate links and brand deals. I sold around 240 units for a bag brand last year through TikTok Shop affiliate, but I don't want to handle inventory or shipping myself.\nBD: Do you have a product idea you would want to create?\nClient: Yes, I want to create a small capsule: a crossbody bag or phone charm line with my own color palette and packaging. I can create content, do launch videos, livestreams, and styling content.\nBD: Do you have a team or budget for product development?\nClient: I don't have budget for inventory, but I can commit content and promotion if the product fits my audience. I can also provide design references and mood boards.\nBD: What would make this collaboration successful for you?\nClient: I want it to feel like my own brand, not just a random dropship product. I care about design, packaging, and story.\n""",
        "training_note": "这个客户不是普通 merchant。不要先推独立站建站，应先确认受众、内容能力、产品创意、样品反馈和分佣方式。"
    },
    "Case 3｜Brand：有产品，想要 KOL/KOC 种草，适合 Myyshop / Product Seeding": {
        "expected_route": "Myyshop / Product Seeding + CPS later",
        "expected_level": "B，先小范围 seeding",
        "transcript": """Client Name: PureSip Bottle\nProduct Category: Water bottle / outdoor lifestyle\nInterview Date: Sample\n\nBD: What are you currently selling and where are you selling it?\nClient: We sell reusable water bottles and outdoor drinkware. We have our own Shopify site and Amazon listing. Amazon does most of the sales, around $15,000 monthly revenue. Shopify is smaller.\nBD: What's your biggest challenge right now?\nClient: Traffic and awareness. The product is good, reviews are good, but we don't have enough creator content. Ads are getting expensive. We want more UGC, reviews, unboxing videos, and maybe micro influencers.\nBD: Do you need sourcing support?\nClient: Not right now. We already have inventory in the U.S. We can provide 100 to 150 samples for creators over the next two months.\nBD: Are you looking for sales conversion or more content exposure?\nClient: First content exposure and product seeding. If some creators perform well, we can set up affiliate commission. We can offer 10% commission after the first test.\nBD: Do you have product assets ready?\nClient: Yes, we have product images, videos, Amazon reviews, and a media kit.\n""",
        "training_note": "这个不是 sourcing case。核心是 seeding/UGC/KOL 内容测试，第一阶段不要承诺大规模 GMV，应先定义 creator profile、样品数量和内容交付。"
    },
    "Case 4｜Merchant：想招代理/分销商，适合 CPL": {
        "expected_route": "MyyBiz CPL / Distributor Lead Gen",
        "expected_level": "B，先跑 lead test",
        "transcript": """Client Name: FitPro Wholesale\nProduct Category: Fitness accessories / resistance bands\nInterview Date: Sample\n\nBD: Tell me a bit about your current business.\nClient: We sell fitness accessories, mainly resistance bands, yoga straps, and small gym accessories. We sell wholesale to local gyms and small retailers. We have a website but it is more like a catalog, not a strong ecommerce store.\nBD: What are you trying to improve next?\nClient: We want to find more resellers and local distributors, especially in California and Texas. Direct consumer sales are not our priority. We need qualified leads, not just traffic.\nBD: Do you have products and pricing ready?\nClient: Yes, we have a wholesale price list, MOQ by SKU, product photos, and shipping terms. We have around 30 SKUs.\nBD: Are you open to paid campaigns?\nClient: We can test $1,000 first if the leads are relevant. We don't want to pay for random clicks, but we can pay for qualified reseller leads.\nBD: What is a good lead for you?\nClient: Gym owners, fitness studios, sports stores, and small distributors. They should have a business email or store information.\n""",
        "training_note": "这个客户的痛点不是普通 CPS，也不是 creator co-creation。关键词是 reseller/distributor/qualified leads，因此优先 CPL。"
    },
    "Case 5｜Low readiness：只有想法，缺产品/预算/渠道，需要 Nurture": {
        "expected_route": "Nurture / Self-service",
        "expected_level": "D/E",
        "transcript": """Client Name: New Starter\nProduct Category: General beauty / trending products\nInterview Date: Sample\n\nBD: What are you currently selling?\nClient: I haven't started yet. I want to sell beauty products because I see a lot of people making money online.\nBD: Do you have a product in mind?\nClient: Not really. Maybe skincare, makeup tools, or something trending on TikTok. I want to see what you can recommend.\nBD: Where are you planning to sell?\nClient: Maybe TikTok or Instagram. I don't have a website yet. I have about 500 followers on Instagram but I don't post much.\nBD: Do you have budget for samples, first order, or ads?\nClient: I prefer not to spend money first. I want to test for free if possible.\nBD: Do you have any sales history or customer list?\nClient: No, this would be my first time.\nBD: Are you interested in MyyBiz or affiliate?\nClient: Maybe, but I don't really know how it works. I just want something easy to make money.\n""",
        "training_note": "这个案例不能因为客户感兴趣就推进。建议发自助教程/爆品清单/教育材料，不进入 sourcing queue。"
    },
    "Case 6｜Gray Compliance：功效护肤/减肥宣称，先审批": {
        "expected_route": "Compliance Review first; CPL only if approved",
        "expected_level": "业务潜力可中高，但合规优先",
        "transcript": """Client Name: GlowFast Lab\nProduct Category: Skincare / body slimming cream\nInterview Date: Sample\n\nBD: What product are you looking to promote?\nClient: We have a body slimming cream and whitening serum. The product page says it can reduce belly fat in 14 days and remove dark spots quickly. We want to run ads and find affiliates to sell it.\nBD: Where are you currently selling?\nClient: We sell through our Shopify store and WhatsApp groups. Monthly revenue is around $6,000, mostly from repeat customers.\nBD: Do you have certificates or ingredient documents?\nClient: We have ingredient list from the supplier, but no U.S. clinical test. We can edit the claims if needed.\nBD: Are you looking for CPC, CPS, or CPL?\nClient: We want CPC ads and affiliates, but if that is difficult, we can start with lead generation.\nBD: Do you have budget?\nClient: Around $800 for testing.\n""",
        "training_note": "这个客户不能直接按高商业价值推进。功效、减肥、美白等宣称必须先合规审批，审批前不建议 CPC/CPS/Stripe。"
    }
}

# -----------------------------
# 1) Rule settings: compliance gate
# -----------------------------
RED_KEYWORDS = [
    "毒品", "违禁药", "武器", "枪", "弹药", "烟草", "电子烟", "vape", "成人内容", "色情", "赌博", "博彩",
    "仿牌", "假货", "counterfeit", "大麻", "cbd", "thc", "加密理财", "金融服务", "危险化学品", "poison",
]

GRAY_KEYWORDS = [
    "保健品", "膳食补剂", "补剂", "减肥", "瘦身", "美容仪", "微整", "医疗器械", "成人向", "不露骨",
    "烟具配件", "博彩娱乐周边", "功效护肤", "祛痘", "美白", "抗衰", "丰胸", "medical", "health claim",
]

GREEN_KEYWORDS = [
    "服装", "帽子", "家居", "家饰", "美妆", "护肤", "3c", "手机壳", "宠物用品", "母婴", "运动户外",
    "饰品", "箱包", "食品", "非保健", "玩具", "文具", "礼品", "茶具", "滤茶器",
]

CHANNEL_MATRIX = {
    "Red": {"Stripe": "❌", "CPC": "❌", "CPS": "❌", "CPL": "❌"},
    "Gray": {"Stripe": "⚠️ 需审批", "CPC": "❌", "CPS": "⚠️ 审批后慎用", "CPL": "✅ 优先"},
    "Green": {"Stripe": "✅", "CPC": "✅ 有预算才做", "CPS": "✅", "CPL": "✅"},
}


def keyword_hit(text: str, keywords: list[str]) -> list[str]:
    text = (text or "").lower()
    return [kw for kw in keywords if kw.lower() in text]


def compliance_decision(product_name: str, category: str, description: str, manual_flags: list[str]) -> dict:
    text = " ".join([product_name or "", category or "", description or ""])
    red_hits = keyword_hit(text, RED_KEYWORDS)
    gray_hits = keyword_hit(text, GRAY_KEYWORDS)

    if manual_flags:
        if any(flag.startswith("红线") for flag in manual_flags):
            return {
                "level": "Red",
                "label": "🔴 Red / 不通过",
                "reason": "命中人工勾选的红线风险：" + "；".join(manual_flags),
                "need_approval": "No - 直接拒绝或更换品类",
            }
        if any(flag.startswith("灰色") for flag in manual_flags):
            return {
                "level": "Gray",
                "label": "🟡 Gray / 需审批",
                "reason": "命中人工勾选的灰色风险：" + "；".join(manual_flags),
                "need_approval": "Yes - 先审批，默认 CPL 测试",
            }

    if red_hits:
        return {
            "level": "Red",
            "label": "🔴 Red / 不通过",
            "reason": "命中红线关键词：" + "、".join(red_hits),
            "need_approval": "No - 直接拒绝或更换品类",
        }
    if gray_hits:
        return {
            "level": "Gray",
            "label": "🟡 Gray / 需审批",
            "reason": "命中灰色关键词：" + "、".join(gray_hits),
            "need_approval": "Yes - 先审批，默认 CPL 测试",
        }
    return {
        "level": "Green",
        "label": "🟢 Green / 可进入评估",
        "reason": "未命中红线或灰色高风险关键词。仍建议由业务负责人最终确认。",
        "need_approval": "No",
    }


def score_option(label: str, options: dict[str, int], key: str, help_text=None) -> int:
    selected = st.selectbox(label, list(options.keys()), key=key, help=help_text)
    return options[selected]


def grade(score: float) -> str:
    if score >= 85:
        return "A / Fast Track"
    if score >= 70:
        return "B / 可推进"
    if score >= 55:
        return "C / 小测试验证"
    if score >= 40:
        return "D / 只做轻量跟进"
    return "E / 暂缓或劝退"


def score_band(score: float) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "E"


def evidence_multiplier(evidence_level: str) -> float:
    mapping = {
        "High：有截图/订单/GMV/后台数据证明（1.00）": 1.00,
        "Medium：客户口述 + 部分材料（0.88）": 0.88,
        "Low：只有口头说法，暂无证明（0.75）": 0.75,
    }
    return mapping[evidence_level]


def recommended_channel(compliance: str, product_score: float, client_score: float, myybiz_score: float) -> str:
    if compliance == "Red":
        return "不推荐任何渠道"
    if compliance == "Gray":
        return "默认 CPL；CPS 需审批后慎用；不建议 CPC/Stripe"
    if client_score >= 75 and product_score >= 70 and myybiz_score >= 70:
        return "CPS + CPL + Stripe；有明确预算时可测 CPC"
    if myybiz_score >= 75 and client_score >= 55:
        return "优先 MyyBiz / CPS / CPL；Stripe 作为收款基础"
    if product_score >= 70 and client_score < 55:
        return "Sourcing 可轻量报价；渠道先 CPL 或 self-service"
    if product_score < 55 and client_score >= 70:
        return "客户不错，但商品不稳；先换品/找替代款，再 CPS/CPL"
    return "CPL 或轻量教育；暂不承诺 CPC/CPS 深度资源"


def final_decision(compliance: str, product_score: float, client_score: float, myybiz_score: float, overall_score: float) -> tuple[str, str]:
    if compliance == "Red":
        return "🔴 Reject / 红线不推进", "合规红线优先于所有分数。建议礼貌拒绝或要求客户更换品类。"
    if compliance == "Gray":
        if overall_score >= 70:
            return "🟡 Compliance Review / 先审批后小测", "灰色品类即使分数高，也不能直接放量。先补合规材料，默认 CPL 小范围验证。"
        return "🟡 Park Until Approved / 暂缓", "灰色品类 + 分数不够强，先不要消耗 sourcing 或投放资源。"
    if overall_score >= 85 and min(product_score, client_score, myybiz_score) >= 65:
        return "🟢 A / Fast Track", "高优先级。建议 BD + Sourcing + AM 联合推进，48小时内完成下一步。"
    if overall_score >= 70:
        return "🟢 B / 可推进", "有价值，但要看短板。建议 7-14 天小测试，不要一开始重投入。"
    if overall_score >= 55:
        return "🟡 C / Test & Validate", "先验证关键假设：预算、MOQ、渠道、素材、销售证据。通过后再升级。"
    if overall_score >= 40:
        return "⚪ D / Nurture", "轻量跟进，发送自助材料或爆品清单，不建议 sourcing 深度介入。"
    return "⚫ E / Disqualify for Now", "当前资源/意愿/证据不足。可委婉劝退，等客户有产品、预算或流量后再进入。"


def build_actions(compliance: str, product_score: float, client_score: float, myybiz_score: float, overall_score: float) -> list[str]:
    actions: list[str] = []
    if compliance == "Red":
        return [
            "礼貌告知该类目暂不支持推进，避免讨论支付、投放或采购细节。",
            "如果客户愿意，要求其更换到合规类目后重新评估。",
            "在 CRM/表格中记录红线原因，避免团队重复跟进。",
        ]
    if compliance == "Gray":
        actions.extend([
            "先收集产品详情、宣称文案、素材、证书/资质，再提交内部审批。",
            "审批前只建议 CPL 或信息收集，不承诺 Stripe、CPC 或 CPS 放量。",
        ])

    if overall_score >= 85:
        actions.extend([
            "安排 15-20 分钟深度 call，确认客户目标、预算、SKU 和时间线。",
            "让 sourcing 团队先拿 2-3 个可替代款/报价，优先附图 + FOB/EXW 价格。",
            "同步 MyyBiz 5分钟 demo 链接，引导客户确认店主/分销两种玩法。",
            "设定 48 小时内的 next step：报价、样品、佣金结构或 Stripe/店铺配置。",
        ])
    elif overall_score >= 70:
        actions.extend([
            "进入 B 类 pipeline，但先小测试，不要投入过多定制开发。",
            "要求客户补齐关键缺口：预算、目标售价、MOQ、销售证据或素材。",
            "推荐 CPS/CPL 先跑通转化；CPC 只有在客户有明确预算时再测。",
        ])
    elif overall_score >= 55:
        actions.extend([
            "先做 Test & Validate：一页问卷 + 3个关键问题 + 1个小任务。",
            "如果客户 3 天内无法补资料，就降为 nurture，不进入 sourcing 排队。",
            "可以发爆品清单或 MyyBiz 自助教程，但不要承诺专属供应链资源。",
        ])
    elif overall_score >= 40:
        actions.extend([
            "只做轻量教育：发送平台介绍、爆品清单或 self-service 指南。",
            "设置低频 follow-up，等客户出现搜索、下单、支付、询盘等行为信号再二次触达。",
        ])
    else:
        actions.extend([
            "委婉劝退：目前不适合深度服务，建议先沉淀产品、预算或流量。",
            "保留客户，但不要进入高优先级 pipeline。",
        ])

    if product_score < 55:
        actions.append("商品短板明显：先确认替代款、目标价、可接受 MOQ 和是否能放弃复杂定制。")
    if client_score < 55:
        actions.append("客户短板明显：先确认真实预算、销售记录和决策人，不急着推 demo。")
    if myybiz_score < 55:
        actions.append("MyyBiz fit 不强：先判断客户是店主、affiliate，还是两者都不适合。")
    return actions


def build_questions(compliance: str, product_score: float, client_score: float, myybiz_score: float) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    if compliance == "Gray":
        sections.append(("合规/审批先问", [
            "这个产品是否涉及任何功效、医疗、健康、减肥、成人属性或敏感宣称？具体文案是什么？",
            "是否有合规证书、检测报告、授权文件、成分表或平台可售证明？",
            "最终投放页/商品详情页会怎么描述？有没有 before/after、治疗、保证效果等表达？",
        ]))

    product_questions = [
        "你要找的是现货、轻定制，还是需要重新开发？",
        "目标采购价、目标零售价、可接受毛利率分别是多少？",
        "首单预算和可接受 MOQ 是多少？如果 MOQ 高一点能不能接受？",
        "是否需要 logo、包装、颜色、材质、尺寸或结构定制？",
        "有没有参考链接、竞品链接、图片、视频或样品？",
        "期望交期是什么？能不能接受样品周期和打样费？",
    ]
    if product_score < 55:
        product_questions.extend([
            "如果原款找不到，是否接受 1-2 个相似替代款？",
            "哪些规格是必须保留的，哪些可以妥协？",
        ])
    sections.append(("商品/Sourcing 必问", product_questions))

    client_questions = [
        "你现在主要在哪些渠道销售：Shopify、Amazon、TikTok Shop、线下、社群，还是其他？",
        "过去 3-6 个月该类目的月 GMV、订单量或最好单品表现大概是多少？可以提供截图吗？",
        "这次项目是否有明确预算？预算更偏采购、广告投放，还是达人/affiliate 佣金？",
        "谁是最终决策人？如果报价合适，最快什么时候可以下单或开始测试？",
        "你现在最大的瓶颈是找货、流量、转化、履约，还是分销管理？",
    ]
    if client_score < 55:
        client_questions.extend([
            "是否愿意先做一个小额测试，而不是马上大规模定制？",
            "如果暂时没有销量证明，有没有已有客户群、社群、达人关系或线下渠道？",
        ])
    sections.append(("客户商业价值必问", client_questions))

    myybiz_questions = [
        "你更想做店主卖自己的货，还是做 affiliate 帮别人推广赚佣金？",
        "如果做店主，你准备让谁帮你推广？预计佣金比例能给多少？",
        "是否已经有 Stripe/公司主体/收款方式？如果没有，谁负责收款和履约？",
        "你有没有产品图、短视频、卖点文案、价格表，能不能直接上架？",
    ]
    if myybiz_score < 55:
        myybiz_questions.extend([
            "你目前有没有可触达的人群？比如社群、粉丝、客户名单、线下渠道或达人朋友？",
            "如果没有货源也没有流量，你是否愿意先从一个具体品类/一个小圈层开始？",
        ])
    sections.append(("MyyBiz / 渠道匹配必问", myybiz_questions))
    return sections



# -----------------------------
# 1.5) Interview transcript auto pre-scoring helper
# This is a lightweight rule-based parser for MVP use.
# It does not call external LLM APIs, so it is safe to run locally.
# -----------------------------
def _contains_any(text, words):
    text = (text or "").lower()
    return any(w.lower() in text for w in words)


def _keyword_count(text, words):
    text = (text or "").lower()
    return sum(1 for w in words if w.lower() in text)


def _extract_money_values(text):
    import re
    if not text:
        return []
    values = []
    patterns = [
        r"\$\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)(\s*[kKmM])?",
        r"([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)(\s*[kKmM])?\s*(?:usd|dollars|美金|美元)",
    ]
    for pat in patterns:
        for num, suffix in re.findall(pat, text):
            try:
                val = float(num.replace(',', ''))
                if suffix.strip().lower() == 'k':
                    val *= 1000
                elif suffix.strip().lower() == 'm':
                    val *= 1000000
                values.append(val)
            except Exception:
                pass
    return values


def analyze_interview_transcript(transcript, product_name='', category=''):
    """Return a draft scoring based on interview text.
    The goal is not to replace human judgment, but to create a consistent first pass.
    """
    text = " ".join([product_name or '', category or '', transcript or '']).lower()
    money = _extract_money_values(text)

    # Evidence level
    if _contains_any(text, ['screenshot', '截图', '后台', 'shopify admin', 'amazon seller', 'tiktok shop后台', '订单截图', 'gmv截图', 'payment record', 'invoice', 'purchase order', 'po ', 'store link', '店铺链接']):
        evidence = 'High：有截图/订单/GMV/后台数据证明（1.00）'
    elif _contains_any(text, ['gmv', 'monthly sales', '月销售', '月gmv', 'orders', '订单', 'followers', '粉丝', '社群', 'budget', '预算', '$']) or money:
        evidence = 'Medium：客户口述 + 部分材料（0.88）'
    else:
        evidence = 'Low：只有口头说法，暂无证明（0.75）'

    # Product / Sourcing Fit
    supplier = 11
    if _contains_any(text, ['现有供应商', 'own supplier', 'supplier already', 'factory already', '已有工厂', '自有工厂', '1688', 'alibaba supplier', 'stable supplier', '稳定供应链']):
        supplier = 15
    elif _contains_any(text, ['no supplier', '没有供应商', 'need supplier', '找不到供应商', '无货源', 'sourcing risk']):
        supplier = 3
    elif _contains_any(text, ['need sourcing', '帮我找货', '需要找货', 'open market', 'public market']):
        supplier = 7

    moq = 11
    if _contains_any(text, ['moq is ok', 'moq acceptable', '接受moq', '首单预算', 'budget is ready', '预算没问题']) or any(v >= 1000 for v in money):
        moq = 15
    if _contains_any(text, ['moq too high', 'moq太高', '预算很小', 'budget is low', 'no budget', '没有预算']):
        moq = 3
    if _contains_any(text, ['no budget', '只想免费', 'free only']):
        moq = 0

    customization = 12
    if _contains_any(text, ['logo', 'packaging', '包装', '颜色', 'color', 'label', '轻定制']):
        customization = 9
    if _contains_any(text, ['material change', '尺寸', '材质', '组合', 'size change', '中度定制']):
        customization = 6
    if _contains_any(text, ['mold', '开模', 'structure', '结构', '功能开发', 'from scratch', '重新开发']):
        customization = 3

    margin = 8
    if _contains_any(text, ['margin', '毛利', 'profit', 'markup', 'target retail', '目标零售价', '采购价', 'selling price']):
        margin = 13
    if _contains_any(text, ['good margin', 'high margin', '毛利充足', '利润充足']):
        margin = 18
    if _contains_any(text, ['low margin', '毛利薄', '价格倒挂', 'no profit', '没利润']):
        margin = 3

    demand = 5
    if _contains_any(text, ['hot product', '爆品', 'trending', 'viral', '市场需求', 'customer demand', '客户要', 'best seller']):
        demand = 12
    elif _contains_any(text, ['competitive', '竞争', 'red ocean', '红海']):
        demand = 9
    if _contains_any(text, ['not sure demand', '需求不确定', '不知道有没有人买']):
        demand = 2

    repeat = 3
    if _contains_any(text, ['repeat', '复购', 'reorder', 'subscription', '消耗品', '长期需求', 'monthly', '每月']):
        repeat = 8
    elif _contains_any(text, ['seasonal', '季节', 'one time', '一次性']):
        repeat = 1

    ops_risk = 7
    if _contains_any(text, ['lightweight', 'small item', '轻小', '不易碎', 'durable']):
        ops_risk = 10
    if _contains_any(text, ['fragile', '易碎', 'heavy', '重货', 'liquid', '液体', 'battery', '电池', 'return risk', '售后多']):
        ops_risk = 4
    if _contains_any(text, ['dangerous goods', 'hazmat', '危险品', '物流不可控']):
        ops_risk = 0

    clarity_count = _keyword_count(text, ['规格', 'spec', '图片', 'image', 'link', '链接', '目标价', 'target price', 'quantity', '数量', 'moq', '交期', 'timeline', 'sample', '样品'])
    if clarity_count >= 6:
        product_clarity = 10
    elif clarity_count >= 4:
        product_clarity = 7
    elif clarity_count >= 2:
        product_clarity = 4
    else:
        product_clarity = 2

    product_score = supplier + moq + customization + margin + demand + repeat + ops_risk + product_clarity

    # Client value
    purchase_intent = 8
    if _contains_any(text, ['ready to order', 'ready to buy', '准备下单', '想下单', 'quote', '报价', 'sample', '样品', 'this week', 'next week', '时间线', 'timeline']):
        purchase_intent = 18
    elif _contains_any(text, ['small test', '小测', 'try first', '先试试']):
        purchase_intent = 13
    if _contains_any(text, ['just looking', '了解一下', 'no plan', '没有计划']):
        purchase_intent = 3

    paid_marketing = 8
    if _contains_any(text, ['fb ads', 'facebook ads', 'google ads', 'tiktok ads', '达人付费', 'influencer budget', '广告预算', 'marketing budget', '投放预算']) or any(v >= 200 for v in money):
        paid_marketing = 18
    elif _contains_any(text, ['small ad test', '小额测试', '小预算']):
        paid_marketing = 13
    if _contains_any(text, ['free only', '只想免费', '不投放', 'no marketing budget']):
        paid_marketing = 2

    sales_history = 3
    if _contains_any(text, ['gmv', 'monthly sales', '月gmv', '月销售', 'orders', '订单', 'sold', '销量']):
        sales_history = 12
    if any(v >= 5000 for v in money) and _contains_any(text, ['gmv', 'sales', '销售']):
        sales_history = 17
    if _contains_any(text, ['no sales', '没有销量', 'new beginner', '纯新手']):
        sales_history = 0

    private_domain = 7
    if _contains_any(text, ['followers', '粉丝', 'community', '社群', 'email list', '客户名单', 'whatsapp group', 'facebook group', 'discord', '达人资源', '线下渠道']):
        private_domain = 15
    if _contains_any(text, ['small network', '少量资源', '小社群']):
        private_domain = 11
    if _contains_any(text, ['no traffic', '没有流量', '没有粉丝', 'no audience']):
        private_domain = 0

    ecommerce = 2
    if _contains_any(text, ['amazon', 'shopify', 'tiktok shop', 'woocommerce']):
        ecommerce = 12
    elif _contains_any(text, ['etsy', 'ebay', 'walmart', 'temu', 'shein', 'independent site', '独立站', '电商平台']):
        ecommerce = 8
    elif _contains_any(text, ['offline', '线下', '社群卖货', '微信群']):
        ecommerce = 5

    materials = 1
    mat_count = _keyword_count(text, ['photo', 'image', '图片', 'video', '视频', '素材', '卖点', 'copy', '价格表', 'product page', 'listing'])
    if mat_count >= 4:
        materials = 10
    elif mat_count >= 2:
        materials = 7
    elif mat_count >= 1:
        materials = 4

    decision_maker = 4
    if _contains_any(text, ['owner', 'founder', 'ceo', 'decision maker', '老板', '创始人', '本人决定', '我可以决定']):
        decision_maker = 10
    elif _contains_any(text, ['partner', 'team need confirm', '需要确认', 'manager approval']):
        decision_maker = 4

    client_score = purchase_intent + paid_marketing + sales_history + private_domain + ecommerce + materials + decision_maker

    # MyyBiz Fit
    role_clarity = 5
    if _contains_any(text, ['store owner', '店主', 'affiliate', '分销', '联盟', 'promoter', 'affiliate marketing']):
        role_clarity = 15
    elif _contains_any(text, ['both', '两种都', '探索']):
        role_clarity = 10

    product_ready = 7
    if _contains_any(text, ['already have product', '已有产品', '有货源', 'inventory', 'stock', 'sku', 'ready to list', '可以上架']):
        product_ready = 20
    elif _contains_any(text, ['category direction', '品类方向', '想做这个类目']):
        product_ready = 14
    if _contains_any(text, ['no product', '没有产品方向']):
        product_ready = 0

    affiliate_network = 7
    if _contains_any(text, ['affiliate', 'influencer', '达人', 'creator', '社群', '粉丝', '客户名单', 'promoter', 'distribution network']):
        affiliate_network = 20
    elif _contains_any(text, ['some contacts', '少量人脉', 'small network']):
        affiliate_network = 14
    if _contains_any(text, ['no network', '没有人脉', 'no audience']):
        affiliate_network = 0

    commission_logic = 5
    if _contains_any(text, ['commission', '佣金', 'cps', 'profit share', '分成']):
        commission_logic = 10
    if _contains_any(text, ['commission rate', '佣金比例', 'can give', '可以给佣金', '利润能覆盖']):
        commission_logic = 15
    if _contains_any(text, ['cannot give commission', '不给佣金', '利润不够']):
        commission_logic = 0

    payment_readiness = 4
    if _contains_any(text, ['stripe', '收款', 'payment account', '公司主体', 'llc', '履约方案']):
        payment_readiness = 10
    if _contains_any(text, ['no stripe', '没有stripe', 'cannot collect payment']):
        payment_readiness = 0

    pain_fit = 5
    if _contains_any(text, ['affiliate management', '分销管理', '建站', 'storefront', 'tracking link', 'commission system', '链接', '独立店铺']):
        pain_fit = 15
    elif _contains_any(text, ['sales page', 'landing page', '轻量销售页']):
        pain_fit = 10

    learning_willingness = 3
    if _contains_any(text, ['open to demo', '愿意demo', 'call', '开会', '马上试用', 'try myybiz']):
        learning_willingness = 5
    if _contains_any(text, ['not interested', '不想学', '不愿操作']):
        learning_willingness = 0

    myybiz_score = role_clarity + product_ready + affiliate_network + commission_logic + payment_readiness + pain_fit + learning_willingness

    raw_overall = round((product_score * 0.40) + (client_score * 0.35) + (myybiz_score * 0.25), 1)
    adjusted_overall = round(raw_overall * evidence_multiplier(evidence), 1)

    return {
        'evidence_level': evidence,
        'product_score': product_score,
        'client_score': client_score,
        'myybiz_score': myybiz_score,
        'raw_overall': raw_overall,
        'adjusted_overall': adjusted_overall,
        'dimension_scores': {
            'supplier': supplier, 'moq': moq, 'customization': customization, 'margin': margin,
            'demand': demand, 'repeat': repeat, 'ops_risk': ops_risk, 'product_clarity': product_clarity,
            'purchase_intent': purchase_intent, 'paid_marketing': paid_marketing, 'sales_history': sales_history,
            'private_domain': private_domain, 'ecommerce': ecommerce, 'materials': materials, 'decision_maker': decision_maker,
            'role_clarity': role_clarity, 'product_ready': product_ready, 'affiliate_network': affiliate_network,
            'commission_logic': commission_logic, 'payment_readiness': payment_readiness, 'pain_fit': pain_fit,
            'learning_willingness': learning_willingness,
        },
        'detected_signals': {
            'money_values': money[:10],
            'red_hits': keyword_hit(text, RED_KEYWORDS),
            'gray_hits': keyword_hit(text, GRAY_KEYWORDS),
        }
    }


# -----------------------------
# 1.6) V5 route recommendation and missing-info engine
# -----------------------------
def detect_signal_flags(transcript):
    text = (transcript or "").lower()
    return {
        "creator_or_influencer": _contains_any(text, ["creator", "influencer", "kol", "koc", "tiktok", "instagram", "youtube", "content creator", "内容创作者", "达人", "网红", "粉丝"]),
        "strong_audience": _contains_any(text, ["followers", "粉丝", "audience", "community", "社群", "email list", "customer list", "whatsapp group", "discord", "telegram"]),
        "merchant_or_brand": _contains_any(text, ["merchant", "brand", "store", "shopify", "amazon", "etsy", "tiktok shop", "独立站", "品牌", "商家", "店铺", "卖家"]),
        "has_product_or_inventory": _contains_any(text, ["sku", "inventory", "stock", "already have product", "已有产品", "有货", "现货", "ready to list", "可以上架", "product images", "listing"]),
        "needs_sourcing": _contains_any(text, ["sourcing", "source", "supplier", "factory", "1688", "alibaba", "找货", "寻源", "供应商", "工厂", "采购"]),
        "needs_store": _contains_any(text, ["storefront", "website", "own site", "independent store", "shopify", "建站", "独立站", "店铺", "网站"]),
        "needs_traffic": _contains_any(text, ["traffic", "exposure", "ads", "ad cost", "paid ads", "流量", "曝光", "广告", "投放", "获客"]),
        "wants_affiliate_or_creator_sales": _contains_any(text, ["affiliate", "commission", "creator", "influencer", "cps", "promoter", "达人", "分销", "佣金", "联盟", "带货"]),
        "wants_reseller_or_distributor": _contains_any(text, ["reseller", "distributor", "agent", "wholesale", "dealer", "cpl", "代理", "分销商", "经销商", "批发"]),
        "wants_kol_seeding": _contains_any(text, ["seeding", "sample", "review", "unboxing", "kol", "koc", "product seeding", "种草", "寄样", "开箱", "测评"]),
        "has_paid_budget": _contains_any(text, ["budget", "marketing budget", "paid ads", "ad spend", "广告预算", "投放预算", "愿意投", "小额测试"]),
        "has_gmv_or_orders": _contains_any(text, ["gmv", "orders", "monthly sales", "sales", "订单", "销量", "月销售", "月gmv"]),
        "has_proof": _contains_any(text, ["screenshot", "store link", "后台", "截图", "店铺链接", "订单截图", "gmv截图", "shopify admin", "amazon seller"]),
        "zero_resource": _contains_any(text, ["no product", "no traffic", "no budget", "没有产品", "没有流量", "没有预算", "纯新手"]),
        "compliance_sensitive": bool(keyword_hit(text, RED_KEYWORDS) or keyword_hit(text, GRAY_KEYWORDS)),
    }


def recommend_routes(transcript, draft):
    flags = detect_signal_flags(transcript)
    ds = draft.get('dimension_scores', {})
    routes = []

    def clamp(x):
        return max(0, min(100, int(round(x))))

    # Scores combine explicit signals with existing dimension scores.
    myybiz_store_score = 20 + ds.get('product_ready', 0) * 2 + ds.get('ecommerce', 0) * 2 + ds.get('materials', 0) * 2 + (15 if flags['needs_store'] else 0)
    cpc_score = 20 + ds.get('paid_marketing', 0) * 3 + ds.get('product_ready', 0) + (20 if flags['needs_traffic'] else 0) + (10 if flags['merchant_or_brand'] else 0)
    cpl_score = 20 + (35 if flags['wants_reseller_or_distributor'] else 0) + ds.get('client_score', 0) if False else 0
    cpl_score = 20 + (35 if flags['wants_reseller_or_distributor'] else 0) + ds.get('purchase_intent', 0) + ds.get('private_domain', 0) + (10 if flags['merchant_or_brand'] else 0)
    cps_score = 20 + (30 if flags['wants_affiliate_or_creator_sales'] else 0) + ds.get('commission_logic', 0) * 2 + ds.get('affiliate_network', 0) + ds.get('product_ready', 0)
    cocreation_score = 15 + (30 if flags['creator_or_influencer'] else 0) + (25 if flags['strong_audience'] else 0) + (15 if _contains_any(transcript, ['design', 'creative', 'idea', 'personal brand', 'co-create', '联名', '创意', '个人品牌']) else 0) + (10 if not flags['has_product_or_inventory'] else 0)
    myyshop_score = 15 + (25 if flags['wants_kol_seeding'] else 0) + (15 if flags['merchant_or_brand'] else 0) + ds.get('materials', 0) * 2 + ds.get('product_ready', 0)
    sourcing_score = 20 + (30 if flags['needs_sourcing'] else 0) + draft.get('product_score', 0) * 0.45 + ds.get('product_clarity', 0) * 2
    nurture_score = 15 + (40 if flags['zero_resource'] else 0) + (20 if draft.get('adjusted_overall', 0) < 55 else 0) + (15 if draft.get('evidence_level', '').startswith('Low') else 0)

    route_defs = [
        ("MyyBiz Store", myybiz_store_score, "客户有产品或店铺基础，需要独立站/销售页/商品管理。", "给 5 分钟 MyyBiz store demo，确认产品素材、价格、库存和收款设置。"),
        ("MyyBiz CPC", cpc_score, "客户有产品/店铺且缺流量，愿意投放或已有广告预算。", "先确认预算、目标 CPA/ROAS、素材准备度；预算不清前不要承诺投放。"),
        ("MyyBiz CPL", cpl_score, "客户想招 reseller/distributor/agent，适合 lead generation。", "确认目标代理画像、地区、表单字段、筛选标准和 lead follow-up 责任人。"),
        ("MyyBiz CPS / Affiliate", cps_score, "客户想用达人/affiliate/commission 带货，且有佣金空间。", "确认佣金比例、产品利润、可寄样数量、创作者画像和追踪链接。"),
        ("Co-Creation", cocreation_score, "客户偏 creator，有受众/内容/创意，但缺供应链和履约。", "确认受众画像、内容能力、产品创意、IP/设计参与度和 launch 节奏。"),
        ("Myyshop / Product Seeding", myyshop_score, "客户是品牌/商家，需要 KOL/KOC 内容种草、寄样、曝光。", "确认样品数量、目标平台、内容形式、KOL画像、预算或可接受成本。"),
        ("Sourcing Support", sourcing_score, "客户主要痛点是找货、供应商、价格、MOQ 或定制。", "先拿 2-3 个款式/报价；同时确认目标价、MOQ、定制范围和交期。"),
        ("Nurture / Self-service", nurture_score, "客户信息或资源不足，暂不适合深度投入。", "发自助材料/爆品清单；等出现搜索、下单、预算或素材后再二次触达。"),
    ]
    for name, score, reason, next_action in route_defs:
        routes.append({
            "推荐路线": name,
            "适配分": clamp(score),
            "适配原因": reason,
            "下一步动作": next_action,
        })
    routes = sorted(routes, key=lambda x: x["适配分"], reverse=True)
    if flags['compliance_sensitive']:
        for r in routes:
            r["下一步动作"] = "先做合规/审批确认；审批通过前仅可轻量沟通。" if r["推荐路线"] != "Nurture / Self-service" else r["下一步动作"]
    return routes, flags


def missing_info_from_transcript(transcript):
    text = (transcript or "").lower()
    checks = [
        ("主营品类 / 具体产品", ['category', 'product', '品类', '产品', 'sku']),
        ("销售渠道", ['shopify', 'amazon', 'etsy', 'tiktok shop', 'own site', 'where are you selling', '销售渠道', '平台', '独立站']),
        ("GMV / 订单量 / 生意规模", ['gmv', 'orders', 'monthly sales', '订单', '销量', '月销售', '生意规模']),
        ("销售证明 / 店铺链接 / 后台截图", ['screenshot', 'store link', 'shopify admin', '截图', '店铺链接', '后台']),
        ("目标采购价 / 零售价 / 毛利", ['target price', 'purchase price', 'retail price', 'margin', '目标价', '采购价', '零售价', '毛利']),
        ("MOQ / 首单预算", ['moq', 'minimum order', 'budget', '首单', '预算', '起订量']),
        ("定制范围", ['custom', 'logo', 'packaging', 'material', 'size', '定制', '包装', '材质', '尺寸']),
        ("流量来源 / 私域 / 达人资源", ['traffic', 'followers', 'community', 'influencer', '流量', '粉丝', '社群', '达人', '客户名单']),
        ("营销预算 / 广告经验", ['paid ads', 'ad spend', 'marketing budget', '广告', '投放', '预算']),
        ("佣金比例 / Affiliate 结构", ['commission', 'affiliate', 'cps', '佣金', '分销', '联盟']),
        ("收款 / Stripe / 履约准备", ['stripe', 'payment', 'fulfillment', '收款', '履约', '物流']),
        ("最大痛点", ['challenge', 'headache', 'pain', 'bottleneck', '难题', '痛点', '瓶颈']),
    ]
    missing = []
    present = []
    for item, words in checks:
        if _contains_any(text, words):
            present.append(item)
        else:
            missing.append(item)
    return present, missing


def build_closing_confirmation(missing):
    qmap = {
        "主营品类 / 具体产品": "Your main product/category is ___, correct?",
        "销售渠道": "Your current main sales channel is ___, right?",
        "GMV / 订单量 / 生意规模": "Roughly, is this currently test orders or stable monthly volume?",
        "销售证明 / 店铺链接 / 后台截图": "If we move forward, could you share a simple store link or screenshot so our team can prioritize it?",
        "目标采购价 / 零售价 / 毛利": "Do you have a target purchase price and retail price range in mind?",
        "MOQ / 首单预算": "What first-order quantity or MOQ would feel comfortable for you?",
        "定制范围": "Are you looking for existing products, light customization, or full custom development?",
        "流量来源 / 私域 / 达人资源": "Do you already have creators, communities, customer groups, or offline channels that can help promote?",
        "营销预算 / 广告经验": "Would you be open to a small paid test, or are you mainly looking for organic/affiliate growth first?",
        "佣金比例 / Affiliate 结构": "If we use affiliates or creators, what commission range could work after your cost?",
        "收款 / Stripe / 履约准备": "Do you already have Stripe/payment and fulfillment figured out, or would you need support there?",
        "最大痛点": "If you had to pick one biggest bottleneck right now, is it sourcing, traffic, conversion, logistics, or trust?",
    }
    return [qmap[m] for m in missing[:6] if m in qmap]



def _score_strength(score):
    if score >= 75:
        return "强"
    if score >= 55:
        return "中等"
    return "弱"


def _safe_join(items, default="暂无明显信号"):
    return "、".join(items) if items else default


def build_customer_snapshot(flags, draft, present, missing):
    """Turn raw scores into a human-readable BD snapshot."""
    strengths = []
    risks = []
    if draft.get('product_score', 0) >= 70:
        strengths.append("商品/供应链方向相对清楚")
    elif draft.get('product_score', 0) < 55:
        risks.append("商品需求或 sourcing 可行性还不够清楚")
    if draft.get('client_score', 0) >= 70:
        strengths.append("客户商业价值较高")
    elif draft.get('client_score', 0) < 55:
        risks.append("客户预算、销量或决策信号不足")
    if draft.get('myybiz_score', 0) >= 70:
        strengths.append("MyyBiz/渠道匹配度较高")
    elif draft.get('myybiz_score', 0) < 55:
        risks.append("MyyBiz 角色、分销资源或佣金结构不清")
    if flags.get('has_gmv_or_orders'):
        strengths.append("访谈中提到 GMV/订单表现")
    if flags.get('has_paid_budget'):
        strengths.append("有营销预算或愿意做付费测试")
    if flags.get('has_proof'):
        strengths.append("有可验证材料信号")
    if flags.get('zero_resource'):
        risks.append("客户可能缺产品、缺流量或缺预算")
    if draft.get('evidence_level','').startswith('Low'):
        risks.append("目前证据偏弱，不能按客户口述直接高优先级推进")
    if flags.get('compliance_sensitive'):
        risks.append("存在合规敏感信号，审批优先")
    return {
        "strengths": strengths[:5],
        "risks": risks[:5],
        "present": present,
        "missing": missing,
    }


def build_personalized_plan(top_route, flags, draft, present, missing):
    route = top_route.get("推荐路线", "Nurture / Self-service")
    evidence = draft.get('evidence_level','')
    product_s = draft.get('product_score', 0)
    client_s = draft.get('client_score', 0)
    myybiz_s = draft.get('myybiz_score', 0)
    overall = draft.get('adjusted_overall', 0)
    snapshot = build_customer_snapshot(flags, draft, present, missing)

    if flags.get('compliance_sensitive'):
        priority = "先合规，再业务推进"
    elif overall >= 85:
        priority = "Fast Track，但要锁定一个具体 next step"
    elif overall >= 70:
        priority = "可推进，小范围验证后再加资源"
    elif overall >= 55:
        priority = "先补证据和关键信息，不急着投入"
    else:
        priority = "轻量 nurture，暂不进入 deep sourcing"

    route_config = {
        "MyyBiz Store": {
            "angle": "不要先讲所有功能，先把客户的产品上架和收款链路跑通。",
            "step1": "确认 1-3 个最适合先上架的 SKU、目标售价、库存/供应方式和素材完整度。",
            "step2": "安排 5 分钟 store demo，只展示商品上传、价格、订单和 affiliate 链接，不做大而全介绍。",
            "step3": "让客户在 48 小时内补齐产品图/视频/卖点/价格表；资料齐再进入店铺搭建。",
            "talk": "Based on what you shared, I don’t think we need to overcomplicate this. The best next step is to pick 1-3 products and see whether we can quickly turn them into a simple store flow. If that works, we can add affiliate or traffic support later.",
        },
        "MyyBiz CPC": {
            "angle": "客户缺流量时，先验证预算、素材和目标，不要直接承诺投放结果。",
            "step1": "确认月预算区间、目标 CPA/ROAS、目标地区和主推 SKU。",
            "step2": "检查素材是否能投放：图片/视频/落地页/卖点/价格是否完整。",
            "step3": "建议先做小额 7-14 天 test，结果达标再扩量。",
            "talk": "Since your main bottleneck seems to be traffic, I’d suggest we start with a small test instead of a big campaign. First we need to confirm your budget range, target product, and whether the creative materials are ready.",
        },
        "MyyBiz CPL": {
            "angle": "客户想招代理/分销商时，重点不是曝光，而是 lead 质量和后续跟进能力。",
            "step1": "定义目标 lead：地区、角色、采购能力、类目兴趣、最低合作门槛。",
            "step2": "确认 lead 表单字段和客户内部谁负责 24-48 小时内跟进。",
            "step3": "先小范围收集 lead，复盘有效率后再扩大投放。",
            "talk": "If the goal is to find resellers or distributors, I’d treat this as a lead quality project, not just a traffic project. We should first define what a qualified partner looks like and who will follow up once leads come in.",
        },
        "MyyBiz CPS / Affiliate": {
            "angle": "客户想用达人/affiliate 带货时，先看佣金空间、样品能力和素材，而不是先找一堆达人。",
            "step1": "确认可给佣金比例、毛利空间、样品数量和可接受履约方式。",
            "step2": "确定 creator/affiliate 画像：平台、粉丝量级、内容风格、目标人群。",
            "step3": "先跑 3-5 个小样本 creator/affiliate，验证点击、内容质量和首单转化。",
            "talk": "This sounds more suitable for a performance-based affiliate test. Before we bring creators in, we should make sure the commission, sample plan, and product story are clear enough for them to promote.",
        },
        "Co-Creation": {
            "angle": "Creator 型客户不要一上来推店铺功能，要先确认个人品牌、受众和产品创意是否能成立。",
            "step1": "确认 creator 的受众画像、内容平台、内容风格和过往转化案例。",
            "step2": "把产品想法收敛成 1 个 hero product，不要同时开发太多款。",
            "step3": "明确分工：creator 负责创意/内容/推广，DHgate 评估开发、样品、生产和履约。",
            "talk": "For you, I’d think about this less as a normal store setup and more as a co-created product launch. The key is whether we can match your audience with one product idea that feels authentic to your brand.",
        },
        "Myyshop / Product Seeding": {
            "angle": "品牌想做 KOL/KOC 曝光时，先确认样品、内容目标和 KOL 画像，避免泛泛寄样。",
            "step1": "确认样品数量、目标平台、内容形式和目标 KOL/KOC 画像。",
            "step2": "明确内容目标：曝光、测评、UGC、直播、转化，不能所有都要。",
            "step3": "先做一小批 seeding，看内容质量和反馈，再决定是否扩大。",
            "talk": "If your goal is creator content and exposure, I’d start with a controlled seeding test. We should define what kind of creators and what kind of content you actually want before sending samples out.",
        },
        "Sourcing Support": {
            "angle": "Sourcing 型客户不要先推 MyyBiz，要先把商品、目标价、MOQ、定制边界问清楚。",
            "step1": "让客户确认目标采购价、目标零售价、MOQ、交期和是否接受相似替代款。",
            "step2": "Sourcing 只先找 2-3 个可比款/报价，避免一开始深度开发。",
            "step3": "如果报价被客户接受，再讨论 MyyBiz 上架、CPS/CPL 或 Stripe。",
            "talk": "It sounds like the first priority is sourcing, not a full marketing setup yet. I’d suggest we first validate whether we can find the right product at the right price and MOQ, then decide which sales channel makes sense.",
        },
        "Nurture / Self-service": {
            "angle": "信息不足或资源不足时，保持关系，但不要投入高成本资源。",
            "step1": "给客户一个低门槛任务：补 1 个产品方向、1 个销售渠道、1 个预算范围。",
            "step2": "发送自助教程/爆品清单/案例，不安排 sourcing 深度开发。",
            "step3": "等客户出现下单、预算、素材、店铺链接或明确需求后再升级。",
            "talk": "I think it may be better to start lighter for now. If you can share a clearer product direction, rough budget, or current selling channel, I can better decide what resources are actually useful for you.",
        },
    }
    cfg = route_config.get(route, route_config["Nurture / Self-service"])

    if flags.get('compliance_sensitive'):
        first_step = "先暂停渠道/投放/收款承诺，补合规材料并提交审批。"
    elif evidence.startswith('Low'):
        first_step = "先补可验证材料：店铺链接、销量截图、产品素材、预算范围或样品图。"
    elif product_s < 55:
        first_step = "先补商品信息：参考链接、目标价、MOQ、定制要求和交期。"
    elif client_s < 55:
        first_step = "先确认客户真实意愿：预算、决策人、销售记录和时间线。"
    elif myybiz_s < 55:
        first_step = "先确认客户到底是店主、affiliate、creator，还是只需要 sourcing。"
    else:
        first_step = cfg["step1"]

    do_not = []
    if evidence.startswith('Low'):
        do_not.append("不要因为客户口述 GMV/粉丝/资源就直接给 A 类优先级。")
    if flags.get('compliance_sensitive'):
        do_not.append("审批前不要承诺 Stripe、CPC、CPS 放量或具体收益。")
    if product_s < 55:
        do_not.append("商品没讲清楚前，不要让 sourcing 团队做深度开发。")
    if client_s < 55:
        do_not.append("客户意愿/预算不清前，不要安排太多内部资源。")
    if myybiz_s < 55:
        do_not.append("不要强推 MyyBiz 全套功能，先判断客户真实角色。")
    if not do_not:
        do_not.append("不要一次性介绍所有产品线，只讲与客户当前痛点最相关的一条路径。")

    return {
        "priority": priority,
        "route": route,
        "angle": cfg["angle"],
        "why": top_route.get("适配原因", "基于访谈信号和评分结果。"),
        "first_step": first_step,
        "next_steps": [first_step, cfg["step2"], cfg["step3"]],
        "talk_track": cfg["talk"],
        "strengths": snapshot["strengths"],
        "risks": snapshot["risks"],
        "do_not": do_not,
    }


def build_personalized_followup_questions(plan, missing):
    base = []
    route = plan.get('route','')
    if "Sourcing" in route:
        base = [
            "Could you send 1-2 reference links or images so our sourcing team can match the exact style?",
            "What target purchase price and first-order quantity would make this worth testing for you?",
            "Which parts are must-have versus flexible — logo, packaging, material, size, or color?",
        ]
    elif "CPC" in route:
        base = [
            "What monthly test budget would feel comfortable for the first 7-14 days?",
            "Which product would you want to push first, and what result would count as success for you?",
            "Do you already have videos/images/landing page ready for paid traffic?",
        ]
    elif "CPL" in route:
        base = [
            "What does a qualified reseller/distributor look like for you?",
            "Which regions or customer segments should we target first?",
            "Who on your side will follow up with leads within 24-48 hours?",
        ]
    elif "CPS" in route or "Affiliate" in route:
        base = [
            "What commission range can your margin support after product and fulfillment cost?",
            "How many samples can you provide for the first creator/affiliate test?",
            "What creator profile fits your product best — platform, niche, audience, and content style?",
        ]
    elif "Co-Creation" in route:
        base = [
            "What product idea feels most authentic to your audience and personal brand?",
            "Can you share your audience profile and best-performing content examples?",
            "How involved do you want to be in design, sampling review, and launch promotion?",
        ]
    elif "Myyshop" in route:
        base = [
            "What content outcome matters most: UGC, review, unboxing, livestream, or conversion?",
            "How many samples can you provide for the first seeding batch?",
            "Which creator niche and platform are the best match for this product?",
        ]
    else:
        base = [
            "What is the one product/category you want to test first?",
            "What channel are you currently using to reach customers?",
            "What rough budget or resource can you commit to the first small test?",
        ]

    missing_qs = build_closing_confirmation(missing)
    combined = base + [q for q in missing_qs if q not in base]
    return combined[:6]


# -----------------------------
# 2) UI
# -----------------------------
st.title("🧭 Sourcing & Client Qualification Tool V8.1")
st.caption("基于 Handbook + Live Conversation Toolkit 优化：自然访谈输入 → 后台信号抽取 → benchmark 评分 → 路线推荐 → Missing Info → 个性化推荐动作与话术。V8 新增 sample cases，方便员工练习和校准判断。V8.1 增加项目致谢。")


with st.expander("项目致谢 Acknowledgements", expanded=False):
    st.markdown(
        """
        - **Handbook input:** Special thanks to **Frank** and **Jack** for their input on the DHgate MyyBiz SP Follow-up Handbook.
        - **Live Conversation Toolkit input:** Special thanks to **Ouna** for her input on the Live Conversation & Interview Toolkit.

        These inputs helped shape the tool's interview flow, scoring benchmarks, route recommendation, and personalized follow-up logic.
        """
    )

with st.expander("V8 逻辑说明", expanded=False):
    st.write(
        """
        - 合规 Red/Gray/Green 是硬闸门，不被分数覆盖。
        - 分数不是绝对真理，是为了让 BD / Sourcing / AM 对优先级有统一语言。
        - 新增 Evidence Level：如果客户只是口头说，没有截图/订单/GMV，综合分会打折，避免假高分。
        - V6 优化：评分选项从“好/一般/差”改成更具体的业务阈值，例如 GMV、订单量、粉丝/名单规模、预算区间、毛利率、响应时效、SKU 准备度。
        - V7 优化：推荐动作不再只套模板，会根据客户 transcript 里的痛点、证据、短板、路线生成更个性化的 follow-up plan 和话术。
        - V8 新增：内置 6 个 sample interview cases，覆盖 Seller / Creator / Brand / Distributor / Nurture / Gray compliance，帮助新员工练习判断。
        - Route Recommendation：判断客户更适合 MyyBiz Store / CPC / CPL / CPS / Co-Creation / Myyshop / Sourcing / Nurture。
        """
    )



with st.expander("评分 Benchmark：不同人怎么选才一致", expanded=True):
    st.markdown(
        """
        **V7 的原则：先用阈值统一判断，再结合客户信号生成个性化建议。**  
        使用者不需要手填 73、82 这种自由数字，而是选择最接近事实的 benchmark。
        例如：月 GMV、订单量、粉丝/名单规模、广告预算、毛利率、MOQ 与预算倍率、响应时间、SKU/素材准备度。

        **统一判断规则：**
        1. 只有客户满足该档位的具体条件，才选该档位。
        2. 没有截图、订单、GMV、广告后台、店铺链接、素材等证明时，不要选最高档。
        3. 粉丝数不能单独算高分，必须看是否可触达、是否有互动、是否愿意配合转化。
        4. 介于两档之间时，先选较低档，再把缺口放进“下一步要问客户的问题”。
        5. Red / Gray 合规闸门优先于所有分数，不能因为客户分数高就绕过。
        """
    )
    tab_a, tab_b, tab_c, tab_d = st.tabs(["商品/Sourcing", "客户商业价值", "MyyBiz Fit", "证据与动作"])
    with tab_a:
        st.dataframe(pd.DataFrame([
            {"维度": "供应商可得性", "高分 benchmark": "24-48h 可拿 2-3 个报价", "中分 benchmark": "48-72h 可找相似款", "低分 benchmark": ">5 个工作日新开发/无源"},
            {"维度": "MOQ & 预算", "高分 benchmark": "MOQ 金额 ≤ 首单预算", "中分 benchmark": "MOQ 为预算 1.0-1.5x，可谈", "低分 benchmark": "MOQ 超预算 >2x/只想免费样"},
            {"维度": "毛利空间", "高分 benchmark": "落地毛利 ≥40-50%", "中分 benchmark": "毛利 20-40%，需控投放", "低分 benchmark": "毛利 <20% 或倒挂"},
            {"维度": "定制复杂度", "高分 benchmark": "现货/贴标/包装 7-14 天样品", "中分 benchmark": "尺寸/材质/组合调整", "低分 benchmark": "开模/功能开发/从 0 开发"},
            {"维度": "需求清晰度", "高分 benchmark": "图/链接/规格/目标价/MOQ/交期齐", "中分 benchmark": "缺 1-2 个关键参数", "低分 benchmark": "只有品类或爆品想法"},
        ]), use_container_width=True, hide_index=True)
    with tab_b:
        st.dataframe(pd.DataFrame([
            {"维度": "销售表现", "高分 benchmark": "月 GMV ≥$20k 或月订单 ≥300", "中分 benchmark": "$1k-$20k 或少量真实订单", "低分 benchmark": "无销售记录/无计划"},
            {"维度": "营销预算", "高分 benchmark": "月预算 ≥$2k 或稳定投放", "中分 benchmark": "$200-$2k 小测/接受 CPS", "低分 benchmark": "只想免费/不分佣/不投放"},
            {"维度": "私域/流量", "高分 benchmark": "名单 ≥5k 或社媒 ≥50k 且互动 ≥2%", "中分 benchmark": "名单 300-5k 或社媒 2k-50k", "低分 benchmark": "无私域且不愿买流量"},
            {"维度": "电商基础", "高分 benchmark": "运营主流平台 ≥6 个月", "中分 benchmark": "有线上/线下交易经验", "低分 benchmark": "纯新手且不愿学"},
            {"维度": "响应/决策", "高分 benchmark": "本人拍板，24h 内响应", "中分 benchmark": "1-2 天响应，需内部确认", "低分 benchmark": ">3 天响应/决策链不清"},
        ]), use_container_width=True, hide_index=True)
    with tab_c:
        st.dataframe(pd.DataFrame([
            {"维度": "产品准备度", "高分 benchmark": "3+ SKU，7 天内可上架", "中分 benchmark": "1-2 SKU 或品类清楚", "低分 benchmark": "只有泛品类兴趣"},
            {"维度": "分销资源", "高分 benchmark": "≥10 推广伙伴或名单 ≥5k", "中分 benchmark": "1-9 个推广伙伴/愿意外联", "低分 benchmark": "无人脉也不愿开发"},
            {"维度": "佣金结构", "高分 benchmark": "毛利可支撑 15-30% 佣金", "中分 benchmark": "5-15% 佣金需测算", "低分 benchmark": "<5% 或无法给佣金"},
            {"维度": "收款履约", "高分 benchmark": "Stripe/PayPal/主体/履约就绪", "中分 benchmark": "收款或履约需协助", "低分 benchmark": "暂不具备收款/履约"},
            {"维度": "痛点匹配", "高分 benchmark": "建站/分销/affiliate/私域转化", "中分 benchmark": "缺流量或销售页", "低分 benchmark": "痛点主要是物流/价格战"},
        ]), use_container_width=True, hide_index=True)
    with tab_d:
        st.dataframe(pd.DataFrame([
            {"项目": "High Evidence", "定义": "有后台截图、订单、GMV、支付记录、广告截图、店铺链接、商品素材", "处理": "综合分 x 1.00"},
            {"项目": "Medium Evidence", "定义": "客户口述 + 部分材料，例如只有店铺链接或部分产品图", "处理": "综合分 x 0.88"},
            {"项目": "Low Evidence", "定义": "只有口头说法，暂无任何可验证材料", "处理": "综合分 x 0.75"},
            {"项目": "A/B 客户", "定义": "分数高且证据较强", "处理": "安排 deep call、报价、demo、48h next step"},
            {"项目": "C/D 客户", "定义": "有潜力但缺信息或缺行动信号", "处理": "问卷、小测试、低频 nurture"},
            {"项目": "E 客户", "定义": "无产品、无预算、无流量、无执行意愿", "处理": "委婉劝退，不进入 sourcing queue"},
        ]), use_container_width=True, hide_index=True)


st.divider()


st.header("Step 0：Interview Analyzer 自动预评分 + 路线推荐（可选）")
st.caption("把客户访谈记录、call transcript、聊天记录粘进来，系统会先给 draft score，并推荐更适合 MyyBiz Store / CPC / CPL / CPS / Co-Creation / Myyshop / Sourcing / Nurture 哪条路线。这个结果适合做初筛，最终仍建议 BD/Sourcing 人工复核。")

with st.expander("没有真实案例？加载 Sample Case 给员工练习", expanded=False):
    sample_name = st.selectbox("选择一个练习案例", list(SAMPLE_CASES.keys()), key="sample_case_select")
    selected_sample = SAMPLE_CASES[sample_name]
    st.write("**Expected Route：**", selected_sample["expected_route"])
    st.write("**Expected Level：**", selected_sample["expected_level"])
    st.write("**Training Note：**", selected_sample["training_note"])
    if st.button("加载这个案例到 Interview Analyzer", key="load_sample_case"):
        st.session_state["interview_script_input"] = selected_sample["transcript"]
        st.rerun()

interview_script = st.text_area(
    "粘贴 Interview Script / Call Notes / Chat Record",
    placeholder="例如：客户说自己在 Shopify 卖家居品类，月 GMV 约 $8,000，有产品图和视频，愿意先做小额广告测试，需要找轻定制包装，接受 300 MOQ，希望做 affiliate commission...",
    height=180,
    key="interview_script_input",
)

if interview_script.strip():
    draft = analyze_interview_transcript(interview_script, product_name='', category='')
    draft_decision = compliance_decision('', '', interview_script, [])
    draft_status, draft_reason = final_decision(
        draft_decision['level'],
        draft['product_score'],
        draft['client_score'],
        draft['myybiz_score'],
        draft['adjusted_overall'],
    )
    draft_channel = recommended_channel(
        draft_decision['level'],
        draft['product_score'],
        draft['client_score'],
        draft['myybiz_score'],
    )

    st.subheader("自动预评分结果")
    a1, a2, a3, a4, a5 = st.columns(5)
    a1.metric("Compliance", draft_decision['label'])
    a2.metric("商品分", f"{draft['product_score']}/100")
    a3.metric("客户分", f"{draft['client_score']}/100")
    a4.metric("MyyBiz Fit", f"{draft['myybiz_score']}/100")
    a5.metric("证据折扣后", f"{draft['adjusted_overall']}/100", grade(draft['adjusted_overall']))

    st.write("**Draft 状态：**", draft_status)
    st.write("**推荐渠道：**", draft_channel)
    st.write("**判断理由：**", draft_reason)
    st.write("**建议证据等级：**", draft['evidence_level'])

    signal = draft['detected_signals']
    with st.expander("系统识别到的信号 / 为什么这样打分", expanded=False):
        st.write("**命中红线关键词：**", signal['red_hits'] if signal['red_hits'] else "无")
        st.write("**命中灰色关键词：**", signal['gray_hits'] if signal['gray_hits'] else "无")
        st.write("**识别到的金额：**", signal['money_values'] if signal['money_values'] else "无")
        st.dataframe(pd.DataFrame([
            {"评分项": k, "自动分": v} for k, v in draft['dimension_scores'].items()
        ]), use_container_width=True, hide_index=True)

    st.subheader("基于 transcript 的推荐动作")
    for action in build_actions(draft_decision['level'], draft['product_score'], draft['client_score'], draft['myybiz_score'], draft['adjusted_overall']):
        st.write("- " + action)

    st.subheader("基于 transcript 的下一步追问")
    for section_title, questions in build_questions(draft_decision['level'], draft['product_score'], draft['client_score'], draft['myybiz_score']):
        with st.expander(section_title, expanded=False):
            for q in questions:
                st.write("- " + q)

    auto_result = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "interview_transcript_auto_draft",
        "compliance_level": draft_decision['level'],
        "compliance_reason": draft_decision['reason'],
        "evidence_level": draft['evidence_level'],
        "product_score": draft['product_score'],
        "client_score": draft['client_score'],
        "myybiz_score": draft['myybiz_score'],
        "raw_overall": draft['raw_overall'],
        "adjusted_overall": draft['adjusted_overall'],
        "final_status": draft_status,
        "recommended_channel": draft_channel,
    }
    auto_df = pd.DataFrame([auto_result])
    st.download_button(
        "下载 transcript 自动预评分 CSV",
        auto_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="interview_auto_scoring_result_v8.csv",
        mime="text/csv",
    )

st.info("建议用法：Transcript 自动评分只做 first pass。客户如果说有 GMV、粉丝、预算，但没有截图/链接/订单证明，系统会自动给证据折扣；最终推进前仍要人工确认。")

if interview_script.strip():
    st.subheader("V8 路线推荐：客户更适合哪条业务线？")
    routes, flags = recommend_routes(interview_script, draft)
    route_df = pd.DataFrame(routes)
    st.dataframe(route_df, use_container_width=True, hide_index=True)
    top_route = routes[0]
    present, missing = missing_info_from_transcript(interview_script)
    plan = build_personalized_plan(top_route, flags, draft, present, missing)
    st.success(f"系统优先推荐：{top_route['推荐路线']}（适配分 {top_route['适配分']}/100）")
    st.write("**推荐原因：**", top_route["适配原因"])

    st.subheader("V8 个性化推荐动作")
    pc1, pc2 = st.columns([1, 1])
    with pc1:
        st.markdown("**推荐推进策略**")
        st.write(plan["priority"])
        st.markdown("**这次沟通的角度**")
        st.write(plan["angle"])
        st.markdown("**第一步先做什么**")
        st.write(plan["first_step"])
    with pc2:
        st.markdown("**客户强信号**")
        if plan["strengths"]:
            for item in plan["strengths"]:
                st.write("✅ " + item)
        else:
            st.write("暂无明显强信号。")
        st.markdown("**风险/短板**")
        if plan["risks"]:
            for item in plan["risks"]:
                st.write("⚠️ " + item)
        else:
            st.write("暂无明显短板。")

    with st.expander("推荐 next steps + 可直接使用的话术", expanded=True):
        st.markdown("**建议 next steps**")
        for step in plan["next_steps"]:
            st.write("- " + step)
        st.markdown("**Follow-up talk track**")
        st.write(plan["talk_track"])
        st.markdown("**这单暂时不要做什么**")
        for item in plan["do_not"]:
            st.write("- " + item)

    st.subheader("个性化 follow-up questions")
    for q in build_personalized_followup_questions(plan, missing):
        st.write("- " + q)

    mcol1, mcol2 = st.columns(2)
    with mcol1:
        st.markdown("**已抓到的关键信息**")
        if present:
            for item in present:
                st.write("✅ " + item)
        else:
            st.write("暂无明显结构化信息。")
    with mcol2:
        st.markdown("**缺失信息 / 建议追问**")
        if missing:
            for item in missing[:8]:
                st.write("⚠️ " + item)
        else:
            st.write("关键信息较完整。")

    st.subheader("Call 结束前 2-minute closing check")
    closing_qs = build_closing_confirmation(missing)
    if closing_qs:
        for q in closing_qs:
            st.write("- " + q)
    else:
        st.write("- Before I bring this back to the team, let me confirm: the next step is ___, correct?")

with st.expander("自然访谈框架：前台自然聊，后台抓 signal", expanded=False):
    st.markdown("""
    **Opening**  
    Hey [Name], thanks for making the time. This is informal — I mainly want to learn how things are going on your end, then I can share what might be relevant from our side.

    **Business Snapshot**  
    Can you tell me a bit about what you're currently selling and where you're selling it?

    **Growth Pain Point**  
    If you had to pick one biggest headache lately — sourcing, traffic, conversion, logistics, or customer trust — what would it be?

    **Product / Sourcing**  
    For the product you're looking for, are you trying to find something already available, or do you need logo, packaging, or custom development?

    **Channel / MyyBiz Fit**  
    For growth, are you mainly trying to sell more through your own store, or are you also interested in affiliates, creators, or resellers helping you sell?

    **Closing Check**  
    Before I bring this back to the team, let me quickly confirm a few things so I don't miss anything...
    """)

st.divider()

left, right = st.columns([1.1, 1])
with left:
    st.header("Step 1：商品与合规")
    product_name = st.text_input("商品名称", placeholder="例如：滤茶器、手机壳、保健品、美容仪等")
    category = st.text_input("商品类目", placeholder="例如：家居、3C、美妆、母婴、补剂等")
    description = st.text_area("商品描述 / 客户需求", placeholder="客户想做什么？是否定制？是否有功效宣称？是否已有供应商？")
    manual_flags = st.multiselect(
        "人工风险勾选（不确定就先不选）",
        [
            "红线：毒品/武器/烟草/Vape/赌博/仿牌/大麻/CBD/未授权金融",
            "灰色：保健品/补剂/美容仪/医疗器械/功效护肤/成人向但非露骨",
        ],
    )
    decision = compliance_decision(product_name, category, description, manual_flags)

with right:
    st.header("合规判断")
    st.metric("Compliance", decision["label"])
    st.write("**原因：**", decision["reason"])
    st.write("**是否需要审批：**", decision["need_approval"])
    matrix = pd.DataFrame([CHANNEL_MATRIX[decision["level"]]]).T.reset_index()
    matrix.columns = ["渠道", "是否可做"]
    st.dataframe(matrix, use_container_width=True, hide_index=True)

st.divider()

st.header("Step 2：证据可信度")
evidence_level = st.selectbox(
    "客户信息可信度（会影响综合分）",
    [
        "High：有截图/订单/GMV/后台数据证明（1.00）",
        "Medium：客户口述 + 部分材料（0.88）",
        "Low：只有口头说法，暂无证明（0.75）",
    ],
    help="行业里最容易误判的是客户说得很好，但没有真实证明。所以 V2 会给低证据信息自动打折。",
)
evidence_factor = evidence_multiplier(evidence_level)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.header("商品/Sourcing Fit")
    supplier = score_option(
        "供应商可得性（15）",
        {
            "15｜现有供应商/1688/工厂资源，24-48h 可拿到 2-3 个报价（15）": 15,
            "13｜公开市场可找，48-72h 可拿到 ≥2 个可比款/报价（13）": 13,
            "10｜能找到相似款，但供应商稳定性/MOQ/交期需二次确认（10）": 10,
            "7｜只有 1 个弱匹配供应商，质量或价格不确定（7）": 7,
            "4｜需要新开发供应商，预计 >5 个工作日才有明确反馈（4）": 4,
            "0｜无可行货源/高仿侵权/供应链风险不可接受（0）": 0,
        },
        "supplier_v2",
    )
    moq = score_option(
        "MOQ & 预算匹配（15）",
        {
            "15｜MOQ 金额 ≤ 客户首单预算，或 ≤ 其月销售量 25%（15）": 15,
            "13｜MOQ 金额为首单预算 1.0-1.3x，客户明确可接受（13）": 13,
            "10｜MOQ 略高，需谈判/拼单/改相似款解决（10）": 10,
            "7｜MOQ 为预算 1.5-2.0x，除非客户加预算否则难推进（7）": 7,
            "3｜MOQ 超预算 >2x，客户只想小样/极小单（3）": 3,
            "0｜客户无预算/不能接受 MOQ/只想免费拿样（0）": 0,
        },
        "moq_v2",
    )
    customization = score_option(
        "定制/打样复杂度（12）",
        {
            "12｜标准现货，直接采购/上架，无改款（12）": 12,
            "10｜轻定制：贴标/logo/吊牌/简单包装，通常 7-14 天可样品（10）": 10,
            "8｜颜色/尺寸/组合包调整，不改结构，需确认 MOQ（8）": 8,
            "5｜材质/版型/包装结构调整，需打样且可能返工（5）": 5,
            "2｜功能/结构/模具/电子方案开发，周期和成本高（2）": 2,
            "0｜从 0 开发且客户预算/规格不清，暂不建议投入（0）": 0,
        },
        "customization_v2",
    )
    margin = score_option(
        "毛利空间：采购+物流后（18）",
        {
            "18｜落地毛利率 ≥50%，可覆盖物流/售后/10-30%佣金/测试预算（18）": 18,
            "15｜落地毛利率 40-50%，多数营销/分销模式可跑（15）": 15,
            "12｜落地毛利率 30-40%，可做 CPS/CPL，小心 CPC（12）": 12,
            "8｜落地毛利率 20-30%，需靠量或降成本，不建议重投广告（8）": 8,
            "3｜落地毛利率 10-20%，价格敏感，只适合验证需求（3）": 3,
            "0｜毛利 <10% 或倒挂，暂不推荐推进（0）": 0,
        },
        "margin_v2",
    )
    demand = score_option(
        "需求/竞争度（12）",
        {
            "12｜客户已有销量/询盘，且竞品价格带不极度内卷（12）": 12,
            "10｜平台/社媒有明显需求，客户能说清目标人群和差异点（10）": 10,
            "8｜需求存在但竞品多，需要靠内容/渠道差异化（8）": 8,
            "5｜只有趋势感或客户直觉，尚无销售/询盘验证（5）": 5,
            "2｜强红海低价品，缺少差异化或品牌故事（2）": 2,
            "0｜伪需求/客户自己也不确定谁会买（0）": 0,
        },
        "demand_v2",
    )
    repeat = score_option(
        "复购/持续性（8）",
        {
            "8｜消耗品/补充装/月度复购，客户可持续补货（8）": 8,
            "6｜季度/季节性复购，能形成系列上新（6）": 6,
            "4｜低频复购，但可做配件/套装/升级款（4）": 4,
            "2｜单次购买为主，依赖持续拉新（2）": 2,
            "0｜一次性项目/无复购路径（0）": 0,
        },
        "repeat_v2",
    )
    ops_risk = score_option(
        "物流/品控/售后风险（10）",
        {
            "10｜轻小耐用、非敏感品，破损/退货风险低（10）": 10,
            "8｜普通包裹，可标准物流履约，品控点少（8）": 8,
            "6｜有尺寸/颜色/兼容性风险，需要清晰 listing 降低退货（6）": 6,
            "4｜易碎/重货/高退货类，物流和售后成本需单独测算（4）": 4,
            "2｜带电/液体/电池/尖锐/高客诉风险，履约需专项确认（2）": 2,
            "0｜物流或合规履约不可控（0）": 0,
        },
        "ops_risk_v2",
    )
    product_clarity = score_option(
        "需求清晰度（10）",
        {
            "10｜参考图/链接、规格、目标采购价、零售价、MOQ、交期都清楚（10）": 10,
            "8｜缺 1-2 项信息，但产品方向和预算清楚（8）": 8,
            "6｜有参考款和用途，但目标价/MOQ/交期不清（6）": 6,
            "4｜只有品类方向，没有具体 SKU 或规格（4）": 4,
            "2｜只说想找爆品/类似款，无法直接报价（2）": 2,
            "0｜需求完全不清晰或频繁变化（0）": 0,
        },
        "product_clarity_v2",
    )
    product_score = supplier + moq + customization + margin + demand + repeat + ops_risk + product_clarity
    st.metric("商品总分", f"{product_score}/100", grade(product_score))

with col2:
    st.header("客户商业价值")
    purchase_intent = score_option(
        "采购/合作意愿（18）",
        {
            "18｜已确认项目、预算、负责人，预计 0-2 周内下单/上线（18）": 18,
            "15｜有明确需求和预算，预计 30 天内测试（15）": 15,
            "12｜愿意小测，但预算/MOQ/时间线有 1 项未确认（12）": 12,
            "8｜有兴趣但时间线模糊，需二次推动（8）": 8,
            "4｜只是了解/收集信息，没有下一步动作（4）": 4,
            "0｜无真实采购或合作意愿（0）": 0,
        },
        "purchase_intent_v2",
    )
    paid_marketing = score_option(
        "付费营销/增长投入（18）",
        {
            "18｜月营销预算 ≥$2,000，或稳定投 FB/Google/TikTok/达人（18）": 18,
            "15｜月预算 $500-$2,000，可做小规模 CPC/CPS 测试（15）": 15,
            "12｜预算 $200-$500，适合轻量素材/达人/CPL 小测（12）": 12,
            "8｜预算未定，但接受佣金/结果导向 CPS（8）": 8,
            "3｜只想免费资源，暂不愿承担推广成本（3）": 3,
            "0｜明确不投放、不分佣、不提供样品（0）": 0,
        },
        "paid_marketing_v2",
    )
    sales_history = score_option(
        "原渠道销售表现（17）",
        {
            "17｜近 3-6 个月月 GMV ≥$20,000，或稳定月订单 ≥300（17）": 17,
            "15｜月 GMV $5,000-$20,000，或稳定月订单 50-300（15）": 15,
            "12｜月 GMV $1,000-$5,000，已有真实复购/评价（12）": 12,
            "8｜有少量真实订单/测试销售，但未稳定（8）": 8,
            "4｜无销售记录，但有明确渠道、产品和启动计划（4）": 4,
            "0｜纯新手且无计划/无渠道/无数据（0）": 0,
        },
        "sales_history_v2",
    )
    private_domain = score_option(
        "私域/流量基础（15）",
        {
            "15｜自有可触达名单 ≥5,000，或社媒 ≥50k 且互动率约 ≥2%（15）": 15,
            "13｜自有名单 1,000-5,000，或社媒 10k-50k 且有稳定互动（13）": 13,
            "10｜有 3+ 达人/社群/线下渠道可直接触达，能配合测试（10）": 10,
            "7｜少量资源：名单 300-1,000 或社媒 2k-10k，需要培养（7）": 7,
            "4｜几乎没有私域，但愿意用付费广告/达人采买补流量（4）": 4,
            "0｜无私域/无达人/无广告预算，也不愿开发流量（0）": 0,
        },
        "private_domain_v2",
    )
    ecommerce = score_option(
        "电商/建站基础（12）",
        {
            "12｜运营 Shopify/Amazon/TikTok Shop ≥6 个月，懂 listing/订单/售后（12）": 12,
            "10｜做过主流平台但运营不深，基本懂上架和履约（10）": 10,
            "8｜做过 Etsy/eBay/Whatnot/Depop/独立站等，有线上交易经验（8）": 8,
            "5｜主要线下/社群成交，但有收款、发货、客服经验（5）": 5,
            "2｜纯新手但愿意按步骤学习和执行（2）": 2,
            "0｜纯新手且不愿学习/不愿操作（0）": 0,
        },
        "ecommerce_v2",
    )
    materials = score_option(
        "电子物料完备度（10）",
        {
            "10｜主图≥5、短视频≥1、卖点、价格表、规格、FAQ 齐全（10）": 10,
            "8｜图片/卖点/价格基本齐，视频或 FAQ 需补（8）": 8,
            "6｜有可用图片和参考链接，但卖点/价格/规格需整理（6）": 6,
            "3｜只有零散图片或竞品链接，无法直接上架（3）": 3,
            "1｜几乎没有素材，需要从零准备（1）": 1,
            "0｜完全没有素材且客户无法提供（0）": 0,
        },
        "materials_v2",
    )
    decision_maker = score_option(
        "决策人/响应质量（10）",
        {
            "10｜本人可拍板，24h 内响应，能提供资料/确认下一步（10）": 10,
            "8｜核心影响人，需老板确认但能推动，1-2 天内响应（8）": 8,
            "6｜有参与权但非决策人，需内部多轮确认（6）": 6,
            "3｜响应慢>3天，决策链不清，资料经常缺失（3）": 3,
            "0｜无法触达决策人/长期不回复（0）": 0,
        },
        "decision_maker_v2",
    )
    client_score = purchase_intent + paid_marketing + sales_history + private_domain + ecommerce + materials + decision_maker
    st.metric("客户总分", f"{client_score}/100", grade(client_score))

with col3:
    st.header("MyyBiz / 渠道 Fit")
    role_clarity = score_option(
        "角色清晰：店主 or Affiliate（15）",
        {
            "15｜能明确选择：店主卖自己的货 / affiliate 推别人的货（15）": 15,
            "12｜主方向清楚，但也愿意探索另一种角色（12）": 12,
            "8｜理解大概玩法，但还没决定角色（8）": 8,
            "4｜对模式感兴趣，但混淆店主/affiliate/平台职责（4）": 4,
            "0｜完全没想清楚或期待平台全包流量/销售（0）": 0,
        },
        "role_clarity_v2",
    )
    product_ready = score_option(
        "可上架产品准备度（20）",
        {
            "20｜已有 3+ 可售 SKU、货源/价格/库存/素材齐，可 7 天内上架（20）": 20,
            "17｜已有 1-2 个明确 SKU，素材或价格需轻微整理（17）": 17,
            "14｜品类方向清楚，货源/报价需 sourcing 确认（14）": 14,
            "9｜有产品想法但无具体 SKU/供应商/目标价（9）": 9,
            "4｜只有泛品类兴趣，需先选品教育（4）": 4,
            "0｜没有产品方向（0）": 0,
        },
        "product_ready_v2",
    )
    affiliate_network = score_option(
        "分销/达人/人脉基础（20）",
        {
            "20｜已有 ≥10 个达人/分销/社群资源，或私域名单 ≥5,000（20）": 20,
            "17｜已有 3-9 个可触达推广伙伴，愿意给样品/佣金测试（17）": 17,
            "14｜有少量人脉或线下渠道，可先招募 1-3 个试点（14）": 14,
            "9｜没有现成人脉，但愿意投放/外联开发（9）": 9,
            "4｜只有模糊人脉说法，无法提供名单或触达方式（4）": 4,
            "0｜没有推广人脉，也不愿开发/投放（0）": 0,
        },
        "affiliate_network_v2",
    )
    commission_logic = score_option(
        "佣金/利润结构清晰（15）",
        {
            "15｜落地毛利可支撑 15-30% 佣金，且客户已确认规则（15）": 15,
            "12｜可给 10-15% 佣金，利润基本覆盖，需细算成本（12）": 12,
            "9｜可给 5-10% 佣金，只适合低成本 affiliate 测试（9）": 9,
            "5｜佣金意愿不清或利润结构没算过（5）": 5,
            "2｜佣金 <5%，对达人/分销吸引力弱（2）": 2,
            "0｜无法给佣金或毛利不够（0）": 0,
        },
        "commission_logic_v2",
    )
    payment_readiness = score_option(
        "Stripe/收款/履约准备（10）",
        {
            "10｜已有 Stripe/PayPal/主体/税务信息/履约方案，可直接配置（10）": 10,
            "8｜已有主体和收款方向，Stripe/店铺配置需协助（8）": 8,
            "6｜可收款但履约/退货/客服流程未定（6）": 6,
            "3｜收款、履约都需要从零指导（3）": 3,
            "0｜暂不具备合法收款或履约能力（0）": 0,
        },
        "payment_readiness_v2",
    )
    pain_fit = score_option(
        "痛点与 MyyBiz 匹配度（15）",
        {
            "15｜核心痛点=建站/分销/affiliate 管理/私域转化，强匹配（15）": 15,
            "12｜痛点=缺销售页/收款链接/内容承接页，较匹配（12）": 12,
            "9｜痛点=缺流量，可用 CPC/CPS 但需预算和素材（9）": 9,
            "6｜痛点=找货/listing/素材，MyyBiz 可辅助但不是核心解法（6）": 6,
            "3｜痛点=物流/客服/价格战，MyyBiz 只能部分帮助（3）": 3,
            "0｜痛点与 MyyBiz 无关或期待不现实（0）": 0,
        },
        "pain_fit_v2",
    )
    learning_willingness = score_option(
        "学习/执行意愿（5）",
        {
            "5｜愿意 3 天内 demo/建店/补资料并开始测试（5）": 5,
            "4｜愿意 1-2 周内试用，但需要 team 协助（4）": 4,
            "3｜愿意了解，节奏慢，需持续 nurture（3）": 3,
            "1｜只想听概念，不愿操作或补资料（1）": 1,
            "0｜不愿学习、不愿试用、不愿提供信息（0）": 0,
        },
        "learning_willingness_v2",
    )
    myybiz_score = role_clarity + product_ready + affiliate_network + commission_logic + payment_readiness + pain_fit + learning_willingness
    st.metric("MyyBiz Fit 总分", f"{myybiz_score}/100", grade(myybiz_score))

st.divider()

st.header("Step 3：系统建议")
raw_overall = round((product_score * 0.40) + (client_score * 0.35) + (myybiz_score * 0.25), 1)
adjusted_overall = round(raw_overall * evidence_factor, 1)
status, status_reason = final_decision(decision["level"], product_score, client_score, myybiz_score, adjusted_overall)
channel = recommended_channel(decision["level"], product_score, client_score, myybiz_score)

c1, c2, c3, c4 = st.columns(4)
c1.metric("原始综合分", f"{raw_overall}/100")
c2.metric("证据折扣后", f"{adjusted_overall}/100", grade(adjusted_overall))
c3.metric("最终状态", status)
c4.metric("推荐渠道", channel)

st.write("**判断理由：**", status_reason)
st.write("**证据可信度：**", evidence_level)

st.subheader("推荐动作")
for action in build_actions(decision["level"], product_score, client_score, myybiz_score, adjusted_overall):
    st.write("- " + action)

st.subheader("下一步要问客户的问题")
for section_title, questions in build_questions(decision["level"], product_score, client_score, myybiz_score):
    with st.expander(section_title, expanded=True):
        for q in questions:
            st.write("- " + q)

st.divider()

st.header("导出结果")
result = {
    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "product_name": product_name,
    "category": category,
    "compliance_level": decision["level"],
    "compliance_reason": decision["reason"],
    "evidence_level": evidence_level,
    "evidence_factor": evidence_factor,
    "product_score": product_score,
    "client_score": client_score,
    "myybiz_score": myybiz_score,
    "raw_overall": raw_overall,
    "adjusted_overall": adjusted_overall,
    "final_status": status,
    "recommended_channel": channel,
}
result_df = pd.DataFrame([result])
st.dataframe(result_df, use_container_width=True, hide_index=True)
st.download_button(
    "下载本次评估结果 CSV",
    result_df.to_csv(index=False).encode("utf-8-sig"),
    file_name="sourcing_qualification_result_v5.csv",
    mime="text/csv",
)

st.divider()
st.header("批量评分入口（预留）")
st.caption("V2 仍以单个客户评估为主。上传 CSV 可先预览，后续可以把批量自动评分接进来。")
uploaded = st.file_uploader("上传客户/商品 CSV", type=["csv"])
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        st.success("上传成功")
        st.dataframe(df.head(50), use_container_width=True)
    except Exception as e:
        st.error(f"读取失败：{e}")
