# Tailored Resumes — London DS £150k+ Target List

Twelve role-tailored resumes for the **"To apply"** roles in the
`London_DS_Target_List_150k Main` tracker. Each is derived **only** from the
improved base CV (`../base/Hani_Azam_base_CV.md`) — no facts are imported from
any other resume. Tailoring is limited to the summary wording, skills ordering,
and which bullets lead; every metric and claim traces to the base CV.

Formats: Markdown source here; matching Word documents in `docx/`; Google Docs
in the Drive folder **"Tailored Resumes - London DS 150k"**.

| # | Company | Role | Sheet score | Markdown | Fit-to-JD¹ |
|---|---------|------|:-----------:|----------|:----------:|
| 1 | OpenAI | Data Scientist, Safety | 9 | `Hani_Azam_OpenAI_DataScientist_Safety.md` | 8/10 |
| 2 | Citadel Securities | Data Scientist | 7 | `Hani_Azam_CitadelSecurities_DataScientist.md` | 5/10 |
| 3 | Stripe | Data Scientist, EMEA | 6 | `Hani_Azam_Stripe_DataScientist_EMEA.md` | 8/10 |
| 4 | Google DeepMind | Applied Data Scientist | 6 | `Hani_Azam_GoogleDeepMind_AppliedDataScientist.md` | 5.5/10 |
| 5 | The Trade Desk | Data Scientist II | 6 | `Hani_Azam_TheTradeDesk_DataScientistII.md` | 6.5/10 |
| 6 | G-Research | Data Scientist | 6 | `Hani_Azam_GResearch_DataScientist.md` | 6/10 |
| 7 | Spotify | Senior Data Scientist | 6 | `Hani_Azam_Spotify_SeniorDataScientist.md` | 8/10 |
| 8 | Monzo | Senior Data Scientist | 6 | `Hani_Azam_Monzo_SeniorDataScientist.md` | 7/10 |
| 9 | Google | Product Data Scientist (L5) | 6 | `Hani_Azam_Google_ProductDataScientist_L5.md` | 9/10 |
| 10 | Bloomberg | Data Scientist | 6 | `Hani_Azam_Bloomberg_DataScientist.md` | 5/10 |
| 11 | Man Group | Senior DS, Responsible Investment | 5 | `Hani_Azam_ManGroup_SeniorDataScientist_ResponsibleInvestment.md` | 7.5/10 |
| 12 | TikTok | Senior Data Scientist, Operations | 5 | `Hani_Azam_TikTok_SeniorDataScientist_Operations.md` | 9/10 |

¹ Fit-to-JD is an internal adversarial-review score of how well the
candidate's *actual* experience matches each JD — not resume quality. Low
scores (Citadel, DeepMind, Bloomberg) reflect genuine experience gaps the
candidate has no finance / production-ML / deep-NLP background to fill, and
the resumes deliberately do **not** fabricate to close them.

## Excluded from this set

- **XTX Markets** — no live DS role (monitoring only).
- **Revolut**, **QuantumBlack** — in the 15-row Target List but not in the
  apply tracker. Say the word and I'll add them.

## Regenerating

```bash
python3 scripts/md_to_docx.py     # rebuild docx/ from the markdown
python3 scripts/qa_resumes.py      # truthfulness + keyword + ATS checks
```
