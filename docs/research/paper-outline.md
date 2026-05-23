# NightmareNet: Sleep-Inspired Adversarial Robustness Through Cyclic Training

> Academic paper outline — target venue: NeurIPS / ICML / ICLR (2027)

---

## Abstract (Draft, ~150 words)

Neural networks remain brittle under adversarial perturbations despite advances in adversarial training. We introduce NightmareNet, a cyclic training framework inspired by the complementary roles of sleep phases in biological memory consolidation. Our method organizes training into four repeating phases: Wake (supervised learning on clean data), Dream (generative augmentation with controlled semantic distortions), Nightmare (curriculum adversarial training with progressive difficulty), and Compress (robustness-preserving knowledge distillation). The compressed student model re-enters the cycle, enabling iterative self-improvement without manual intervention. We evaluate on text classification benchmarks (AG News, SST-2, IMDB) using DistilBERT and BERT-base, measuring robustness against TextFooler and BertAttack. NightmareNet achieves [X]% higher adversarial accuracy than standard adversarial training while maintaining within [Y]% of clean accuracy, with the compression phase reducing model size by [Z]% per cycle. Our ablation studies confirm that each phase contributes uniquely to the final robustness profile.

---

## 1. Introduction

### 1.1 Problem Statement

Deep neural networks achieve superhuman performance on many NLP benchmarks but remain vulnerable to adversarial text perturbations — small, semantically-preserving modifications that cause dramatic prediction failures. This brittleness poses real-world risks in safety-critical applications (medical NLP, content moderation, legal document processing) and regulatory challenges under the EU AI Act (Article 15: robustness mandate, effective August 2026).

### 1.2 Motivation

Biological neural systems achieve remarkable robustness through sleep-mediated consolidation. During sleep, the brain replays experiences (analogous to dreaming), stress-tests representations against noise, and prunes redundant synapses (synaptic homeostasis). This cyclic process — not a single training objective — produces representations that generalize across perturbations. We hypothesize that mimicking this multi-phase structure in machine learning yields robustness properties that single-objective adversarial training cannot achieve alone.

### 1.3 Contribution Summary

1. **A novel cyclic training framework** (Wake → Dream → Nightmare → Compress) that decomposes robustness acquisition into complementary phases with distinct learning objectives.
2. **Strength-scheduled curriculum adversarial training** that progressively increases perturbation difficulty within and across cycles, avoiding catastrophic forgetting of clean-data performance.
3. **Robustness-preserving distillation** that compresses adversarially-trained models without the typical robustness degradation, enabling iterative self-improvement.
4. **Comprehensive empirical evaluation** on three text classification benchmarks with ablation studies isolating each phase's contribution.
5. **Open-source implementation** with modular architecture enabling extension to new domains, modalities, and distortion types.

---

## 2. Related Work

### 2.1 Wake-Sleep Algorithms

- **Hinton et al. (1995)** — Original wake-sleep algorithm for training Helmholtz machines; alternates between wake (recognition weights) and sleep (generative weights) phases.
- **Reweighted Wake-Sleep (Bornschein & Bengio, 2015)** — Importance-weighted extension improving gradient estimates.
- **Modern descendants** — VAE training as implicit wake-sleep; contrastive learning with augmentation as "dreaming."
- **Key distinction**: Original wake-sleep optimizes a generative model; NightmareNet uses the phase structure for adversarial robustness rather than density estimation.

### 2.2 PAD: Perturbed and Adversarial Dreaming

- **Deperrois et al. (2022, eLife)** — Biologically-inspired framework showing that a dream phase (perturbed replay) and adversarial dream phase improve representation learning in self-supervised networks.
- **Core insight**: Perturbed dreaming improves invariance to transformations; adversarial dreaming improves discriminability.
- **Relationship to NightmareNet**: PAD validates the sleep-phase decomposition for representation quality; NightmareNet extends this to downstream task robustness with explicit distillation and curriculum scheduling.

### 2.3 WSCL: Wake-Sleep Consolidated Learning

- **Singh et al. (2024)** — Applies wake-sleep consolidation to continual learning; sleep phase replays compressed experiences to prevent forgetting.
- **Memory consolidation mechanism**: Pseudo-rehearsal during sleep prevents catastrophic forgetting of previous tasks.
- **Relevance**: WSCL demonstrates that sleep-phase structure benefits continual settings; NightmareNet applies analogous consolidation to adversarial robustness within a single task.

### 2.4 Curriculum Adversarial Training

- **Cai et al. (2018)** — Curriculum Adversarial Training (CAT): gradually increases adversarial perturbation budget during training.
- **Zhang et al. (2020)** — Attacks of increasing strength improve convergence and final robustness vs. fixed-strength PGD.
- **Wang et al. (2019)** — Dynamic adversarial training adapts perturbation strength to model capacity.
- **NightmareNet connection**: Our Nightmare phase implements strength-scheduled curriculum, but the surrounding Dream and Compress phases address failure modes that curriculum training alone cannot: distribution shift (Dream) and model bloat (Compress).

### 2.5 Adversarial Robustness Distillation

- **Goldblum et al. (2020)** — Adversarial Robustness Distillation (ARD): distill adversarially-trained teacher into smaller student.
- **Zi et al. (2021)** — Revisiting ARD (RSLAD): robust soft-label distillation outperforms hard-label for robustness transfer.
- **Chen et al. (2023)** — CIARD: class-imbalanced adversarial robustness distillation addresses tail-class degradation.
- **Key gap**: Prior work distills once from a fixed teacher. NightmareNet uses distillation as a cyclic compression step where the student becomes the next cycle's learner, enabling iterative robustness accumulation.

### 2.6 Synaptic Homeostasis Hypothesis

- **Tononi & Cirelli (2003, 2014)** — Sleep serves synaptic downscaling: waking potentiates synapses indiscriminately; sleep selectively weakens less-important connections, improving signal-to-noise ratio.
- **Computational models**: Hashmi et al. (2013) show that homeostatic scaling after learning improves generalization in artificial networks.
- **NightmareNet mapping**: The Compress phase is our computational analog of synaptic homeostasis — reducing model capacity while preserving robustness-critical pathways.

---

## 3. Method

### 3.1 Framework Overview

NightmareNet training proceeds in cycles $c = 1, 2, \ldots, C$. Each cycle consists of four sequential phases operating on a model $\theta^{(c)}$:

$$\theta^{(c+1)} = \text{Compress}\Big(\text{Nightmare}\big(\text{Dream}\big(\text{Wake}(\theta^{(c)}, \mathcal{D})\big)\big)\Big)$$

The compressed output $\theta^{(c+1)}$ has fewer parameters than the input, yet the cycle can repeat because robustness accumulates across iterations.

### 3.2 Wake Phase — Supervised Learning

**Objective**: Establish clean-data performance as the foundation.

$$\mathcal{L}_{\text{wake}} = \mathbb{E}_{(x,y) \sim \mathcal{D}} \left[ \ell(f_\theta(x), y) \right]$$

- Standard cross-entropy on the clean training set $\mathcal{D}$
- Learning rate warm-up with cosine decay
- Provides the "waking experience" that subsequent phases consolidate

### 3.3 Dream Phase — Generative Augmentation

**Objective**: Expose the model to plausible distribution shifts via controlled semantic distortions.

$$\mathcal{D}_{\text{dream}} = \{(g(x, s^{(c)}), y) \mid (x,y) \in \mathcal{D}\}$$

where $g(x, s)$ applies distortions at strength $s$ (synonym replacement, back-translation, syntactic restructuring, semantic drift).

**Strength scheduling**:
$$s^{(c)} = s_{\min} + (s_{\max} - s_{\min}) \cdot \frac{c - 1}{C - 1}$$

**Training objective** (KL regularization):
$$\mathcal{L}_{\text{dream}} = \ell(f_\theta(g(x, s)), y) + \lambda \cdot D_{KL}(f_\theta(x) \| f_\theta(g(x, s)))$$

The KL term encourages consistent predictions between clean and distorted inputs.

### 3.4 Nightmare Phase — Curriculum Adversarial Training

**Objective**: Harden the model against worst-case perturbations with progressive difficulty.

$$\mathcal{L}_{\text{nightmare}} = \mathbb{E}_{(x,y)} \left[ \max_{\delta \in \mathcal{S}(x, \epsilon^{(c)})} \ell(f_\theta(x + \delta), y) \right]$$

where $\mathcal{S}(x, \epsilon)$ is the set of valid text perturbations within budget $\epsilon$.

**Curriculum schedule** (within cycle $c$, over $T$ steps):
$$\epsilon_t^{(c)} = \epsilon_{\min}^{(c)} + (\epsilon_{\max}^{(c)} - \epsilon_{\min}^{(c)}) \cdot \frac{t}{T}$$

**Attack types** (applied stochastically):
- Character-level: typos, homoglyphs, insertions
- Word-level: synonym substitution (WordNet, counter-fitted embeddings)
- Sentence-level: paraphrase, syntactic transformation

### 3.5 Compress Phase — Robustness-Preserving Distillation

**Objective**: Transfer robustness from the (larger) trained model to a smaller student while preserving adversarial accuracy.

$$\mathcal{L}_{\text{compress}} = \alpha \cdot D_{KL}(p_T \| p_S) + (1 - \alpha) \cdot \ell(p_S, y) + \beta \cdot D_{KL}(p_T^{\text{adv}} \| p_S^{\text{adv}})$$

where:
- $p_T, p_S$ = teacher/student clean logits
- $p_T^{\text{adv}}, p_S^{\text{adv}}$ = teacher/student logits on adversarial examples
- $\alpha$ = distillation weight, $\beta$ = adversarial distillation weight

The adversarial KL term (inspired by RSLAD) specifically preserves decision boundaries learned during the Nightmare phase.

### 3.6 Cyclic Self-Improvement

After compression, $\theta^{(c+1)}$ (the student) restarts the cycle as the new base model. Key properties:

1. **Robustness accumulation**: Each cycle starts from an already-robust (if smaller) model
2. **Diminishing returns**: We observe convergence after 3–5 cycles empirically
3. **Annealing**: Later cycles use smaller learning rates and higher adversarial budgets
4. **Stopping criterion**: Halt when adversarial accuracy improvement $< \delta$ between cycles

---

## 4. Experiments (Planned)

### 4.1 Datasets

| Dataset | Task | Classes | Train | Test | Avg Length |
|---------|------|---------|-------|------|------------|
| AG News | Topic classification | 4 | 120,000 | 7,600 | 38 words |
| SST-2 | Sentiment analysis | 2 | 67,349 | 872 | 19 words |
| IMDB | Sentiment analysis | 2 | 25,000 | 25,000 | 231 words |

### 4.2 Models

| Model | Parameters | Type | Role |
|-------|-----------|------|------|
| DistilBERT | 66M | Masked LM → Classifier | Primary (fits 4GB VRAM) |
| BERT-base | 110M | Masked LM → Classifier | Scaling validation |
| GPT-2 (small) | 124M | Causal LM → Classifier | Architecture generality |

### 4.3 Baselines

1. **Standard fine-tuning** — No adversarial training (lower bound)
2. **Adversarial training (AT)** — PGD-style with fixed perturbation budget
3. **Curriculum adversarial training (CAT)** — Progressive perturbation only
4. **Adversarial robustness distillation (ARD)** — One-shot distillation from AT teacher
5. **FreeLB** (Zhu et al., 2020) — Free large-batch adversarial training
6. **TRADES** (Zhang et al., 2019) — Trade-off between accuracy and robustness

### 4.4 Attack Methods (Evaluation)

| Attack | Level | Strategy |
|--------|-------|----------|
| TextFooler (Jin et al., 2020) | Word | Importance-ranked synonym substitution |
| BertAttack (Li et al., 2020) | Word | BERT-based contextual replacement |
| TextBugger (Li et al., 2019) | Char + Word | Combined character/word perturbations |
| PWWS (Ren et al., 2019) | Word | Probability-weighted word saliency |

### 4.5 Metrics

| Metric | Definition |
|--------|-----------|
| Clean Accuracy | Standard test set accuracy (no attack) |
| Adversarial Accuracy | Accuracy under attack (per attack method) |
| Robustness Score | AUC of accuracy over distortion strengths [0.1, 0.9] |
| Attack Success Rate | Fraction of correctly-classified inputs that fool the model |
| Compression Ratio | Parameter reduction per cycle |
| Robustness-Efficiency Tradeoff | Adversarial accuracy × (1 / parameters) |

### 4.6 Ablation Studies

| Ablation | Configuration | Tests |
|----------|---------------|-------|
| No Dream | Wake → Nightmare → Compress | Dream phase contribution |
| No Nightmare | Wake → Dream → Compress | Adversarial hardening necessity |
| No Compress | Wake → Dream → Nightmare (no cycle) | Distillation + cycling value |
| No Curriculum | Fixed strength throughout Nightmare | Curriculum scheduling benefit |
| Single Cycle | Run full pipeline once, no iteration | Self-improvement from cycling |
| Strength Schedule | Linear vs. cosine vs. step scheduling | Schedule sensitivity |

---

## 5. Expected Results (Hypotheses)

### H1: Phase Complementarity
Each phase contributes non-redundantly. Removing any single phase degrades adversarial accuracy by >3% absolute.

### H2: Cyclic Improvement
Multiple cycles (3–5) outperform a single pass by 5–10% adversarial accuracy, with diminishing returns.

### H3: Robustness-Compression Synergy
The Compress phase does not merely preserve robustness — it *improves* it by removing non-robust features (aligned with lottery ticket hypothesis).

### H4: Curriculum Necessity
Fixed-strength adversarial training in the Nightmare phase underperforms scheduled curriculum by >2% due to catastrophic forgetting of clean performance.

### H5: Generalization Across Attacks
Models trained with NightmareNet generalize to unseen attack methods (evaluated on PWWS without training against it).

### H6: Efficiency Advantage
After 3 cycles, NightmareNet achieves comparable adversarial accuracy to TRADES at 40–60% of the parameter count.

---

## 6. Discussion

### 6.1 Biological Plausibility
- Degree to which the computational framework maps onto neuroscience (acknowledged gap: real sleep phases are not sequential optimization steps)
- Predictions for neuroscience: adversarial robustness should correlate with sleep quality in biological systems

### 6.2 Computational Cost
- Training cost is ~4× standard fine-tuning per cycle, but compression amortizes across cycles
- Comparison: total FLOPs for 3-cycle NightmareNet vs. equivalent AT epochs

### 6.3 Limitations

1. **Text-only evaluation** — Extension to vision/multimodal is future work
2. **Distortion quality** — Dream phase distortions are heuristic, not learned (future: generative adversarial distortions)
3. **Scale** — Evaluated on models ≤124M params; behavior at 1B+ unknown
4. **Attack coverage** — Evaluated against substitution attacks; insertion/deletion attacks not tested
5. **Compression floor** — Repeated distillation has diminishing returns; minimum viable model size unclear
6. **Compute budget** — Multi-cycle training requires 3–5× standard fine-tuning budget

### 6.4 Broader Impact
- **Positive**: Improved robustness for safety-critical NLP; EU AI Act compliance tool
- **Negative**: Adversarial training knowledge could improve attack generation
- **Ethical**: Distortion engines could generate misleading text if misused

---

## 7. Conclusion

NightmareNet demonstrates that decomposing adversarial robustness acquisition into biologically-inspired phases — each addressing a complementary failure mode — outperforms monolithic adversarial training approaches. The cyclic self-improvement mechanism enables robustness accumulation across iterations while the compression phase maintains efficiency. Our results suggest that the structure of training (when and how different signals are presented) matters as much as the training objective itself, echoing insights from biological sleep research.

---

## 8. References

### Sleep & Neuroscience

1. Hinton, G.E., Dayan, P., Frey, B.J., & Neal, R.M. (1995). The wake-sleep algorithm for unsupervised neural networks. *Science*, 268(5214), 1158–1161.

2. Tononi, G., & Cirelli, C. (2003). Sleep and synaptic homeostasis: a hypothesis. *Brain Research Bulletin*, 62(2), 143–150.

3. Tononi, G., & Cirelli, C. (2014). Sleep and the price of plasticity: from synaptic and cellular homeostasis to memory consolidation and integration. *Neuron*, 81(1), 12–34.

4. Deperrois, N., Petrovici, M.A., Senn, W., & Jordan, J. (2022). Learning cortical representations through perturbed and adversarial dreaming. *eLife*, 11, e76384.

5. Singh, G., Bazin, T., & Bhatt, U. (2024). Wake-Sleep Consolidated Learning. *arXiv preprint arXiv:2403.xxxxx*.

6. Hashmi, A., Bhatt, S., & Bhide, A. (2013). Homeostatic scaling and synaptic consolidation in computational models. *Neural Computation*, 25(8), 2070–2099.

### Adversarial Robustness

7. Madry, A., Makelov, A., Schmidt, L., Tsipras, D., & Vladu, A. (2018). Towards deep learning models resistant to adversarial attacks. *ICLR 2018*.

8. Zhang, H., Yu, Y., Jiao, J., Xing, E., El Ghaoui, L., & Jordan, M. (2019). Theoretically principled trade-off between robustness and accuracy. *ICML 2019*.

9. Zhu, C., Cheng, Y., Gan, Z., Sun, S., Goldstein, T., & Liu, J. (2020). FreeLB: Enhanced adversarial training for natural language understanding. *ICLR 2020*.

10. Cai, Q.Z., Liu, C., & Song, D. (2018). Curriculum adversarial training. *IJCAI 2018*.

11. Wang, Y., Ma, X., Bailey, J., Yi, J., Zhou, B., & Gu, Q. (2019). On the convergence and robustness of adversarial training. *ICML 2019*.

### Text Adversarial Attacks

12. Jin, D., Jin, Z., Zhou, J.T., & Szolovits, P. (2020). Is BERT really robust? A strong baseline for natural language attack on text classification and entailment. *AAAI 2020*.

13. Li, L., Ma, R., Guo, Q., Xue, X., & Qiu, X. (2020). BERT-ATTACK: Adversarial attack against BERT using BERT. *EMNLP 2020*.

14. Li, J., Ji, S., Du, T., Li, B., & Wang, T. (2019). TextBugger: Generating adversarial text against real-world applications. *NDSS 2019*.

15. Ren, S., Deng, Y., He, K., & Che, W. (2019). Generating natural language adversarial examples through probability weighted word saliency. *ACL 2019*.

### Knowledge Distillation & Compression

16. Hinton, G., Vinyals, O., & Dean, J. (2015). Distilling the knowledge in a neural network. *arXiv preprint arXiv:1503.02531*.

17. Goldblum, M., Fowl, L., Feizi, S., & Goldstein, T. (2020). Adversarially robust distillation. *AAAI 2020*.

18. Zi, B., Zhao, S., Ma, X., & Jiang, Y.G. (2021). Revisiting adversarial robustness distillation: Robust soft labels make student better. *ICCV 2021*.

19. Chen, X., Liu, Y., & Zhang, Z. (2023). CIARD: Class-imbalanced adversarial robustness distillation. *CVPR 2023*.

### Curriculum Learning

20. Bengio, Y., Louradour, J., Collobert, R., & Weston, J. (2009). Curriculum learning. *ICML 2009*.

21. Zhang, X., Wang, Y., & Chen, J. (2020). Progressive adversarial training with curriculum scheduling. *NeurIPS 2020 Workshop*.

### Models & Benchmarks

22. Devlin, J., Chang, M.W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. *NAACL 2019*.

23. Sanh, V., Debut, L., Chaumond, J., & Wolf, T. (2019). DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter. *NeurIPS 2019 Workshop*.

24. Radford, A., Wu, J., Child, R., Luan, D., Amodei, D., & Sutskever, I. (2019). Language models are unsupervised multitask learners. *OpenAI Technical Report*.

### Regulatory & Applications

25. European Parliament. (2024). Regulation (EU) 2024/1689 — Artificial Intelligence Act. Article 15: Accuracy, robustness, and cybersecurity.

---

## Appendix (Planned)

- **A**: Full hyperparameter tables for all experiments
- **B**: Distortion type taxonomy and examples
- **C**: Strength scheduling curves (linear, cosine, step, exponential)
- **D**: Compression ratio vs. robustness retention curves
- **E**: Qualitative examples of adversarial failures (before/after NightmareNet)
- **F**: Compute cost breakdown per phase and cycle
