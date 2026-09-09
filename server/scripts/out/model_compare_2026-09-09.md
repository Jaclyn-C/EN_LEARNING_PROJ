# 文本模型小样本选型（M0）

- 日期：2026-09-09；候选：glm-4-plus, glm-4-air, glm-4-flash
- 任务：`m0/sample_question_gen.md` 对 2 段材料各生成 2 道单选题（结构化输出）
- 质量粗评：字段齐全度/选项唯一/answer 落在 options 内等 11 项启发式检查（非人工结论）
- 汇总 token：input=4849 output=1863 total=6712

| 模型 | 样本 | 结果 | 重试 | 质量粗评 | 耗时(s) | tokens(in/out) |
|---|---|---|---|---|---|---|
| glm-4-plus | P1 | OK | 0 | 11/11 | 8.9 | 826/302 |
| glm-4-plus | P2 | OK | 0 | 11/11 | 4.6 | 793/345 |
| glm-4-air | P1 | OK | 0 | 9/11 | 4.6 | 826/310 |
| glm-4-air | P2 | OK | 0 | 11/11 | 5.3 | 793/394 |
| glm-4-flash | P1 | OK | 0 | 11/11 | 10.9 | 822/229 |
| glm-4-flash | P2 | OK | 0 | 11/11 | 16.2 | 789/283 |

## 明细（问题与失败原因）

- glm-4-air/P1（9/11）：第1题解析过短；第2题解析过短

## 样例题目（每次运行的第一题，供人工抽查）

### glm-4-plus / P1

According to the legend, how was tea discovered by Emperor Shen Nong?
  选项：He intentionally boiled tea leaves in water | He found tea leaves in his boiling water by accident | He received tea leaves as a gift | He discovered tea while meditating
  answer：He found tea leaves in his boiling water by accident
  解析：解析：根据材料中'Emperor Shen Nong discovered tea by accident around 2737 BC, when a few leaves from a wild tea tree drifted into his pot of boiling water'可知，茶叶是意外飘入沸水的，而非有意为之。选项A、C、D都与材料描述不符。

### glm-4-plus / P2

According to the passage, what do supporters of remote work believe?
  选项：Remote work leads to stronger teamwork | Commute time can be saved through remote work | Office noise helps employees concentrate better | Daily check-ins are unnecessary for remote teams
  answer：Commute time can be saved through remote work
  解析：正确答案是B。材料中明确提到支持者认为'跳过通勤每周可以节省几个小时'。A选项与材料中批评者指出的'团队合作减弱'相矛盾；C选项与材料中'员工在没有办公室噪音时注意力更集中'相反；D选项与材料中'团队设定明确目标并进行简短的每日检查'相悖。

### glm-4-air / P1

According to the legend, how did Emperor Shen Nong discover tea?
  选项：He intentionally boiled tea leaves in water | Leaves from a wild tea tree drifted into his boiling water | He found tea leaves growing near his palace | A servant accidentally added tea leaves to his drink
  answer：Leaves from a wild tea tree drifted into his boiling water
  解析：根据材料内容，

### glm-4-air / P2

According to the passage, what is one benefit of remote work mentioned by supporters?
  选项：Stronger teamwork | Saving hours every week | Reduced risk of loneliness | More spontaneous communication
  answer：Saving hours every week
  解析：正确答案是'Saving hours every week'。根据材料，支持者认为远程工作的好处之一是省去了通勤时间，每周可以节省几个小时。其他选项都是错误的：A项'stronger teamwork'与材料中批评者提到的'weaker teamwork'相反；C项'reduced risk of loneliness'与批评者提到的'risk of loneliness'相反；D项'more spontaneous communication'在材料中未被提及。

### glm-4-flash / P1

Which year is associated with the discovery of tea according to the Chinese legend?
  选项：2737 BC | 2000 BC | 1000 BC | 500 BC
  answer：2737 BC
  解析：根据材料，茶的发现与中国的传说有关，发生在公元前2737年。其他选项都是干扰项，没有在材料中提及。

### glm-4-flash / P2

What is one of the arguments made by supporters of remote work?
  选项：A. It reduces the risk of loneliness. | B. It improves teamwork. | C. It saves employees hours every week. | D. It decreases office noise.
  answer：C. It saves employees hours every week.
  解析：正确选项是C，因为材料中提到支持者认为避免通勤可以每周节省数小时。选项A、B和D都是反对者的观点，或者是材料中未提及的信息。

