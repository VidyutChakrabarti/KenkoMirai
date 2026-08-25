<div align="center">

# KenkoMirai Policy Training

### Opt-in policy experiments against the canonical simulator

<p>
  <img alt="Gymnasium" src="https://img.shields.io/badge/Gymnasium-Environment-101815?style=for-the-badge&logoColor=B8E7D1">
  <img alt="Stable Baselines3" src="https://img.shields.io/badge/PPO-Optional-101815?style=for-the-badge&labelColor=101815&color=365D4D">
</p>

<p>
  <a href="../README.md"><img alt="Project overview" src="https://img.shields.io/badge/BACK-PROJECT_OVERVIEW-B8E7D1?style=for-the-badge&labelColor=101815&color=365D4D"></a>
  <a href="../docs/design-decisions.md"><img alt="Design decisions" src="https://img.shields.io/badge/VIEW-DESIGN_DECISIONS-B8E7D1?style=for-the-badge&labelColor=101815&color=477A65"></a>
</p>

</div>

---

This optional module wraps the same Mesa model used by the API with Gymnasium and trains a two-action PPO policy (`open` or `lockdown`). Disease parameters, validated mobility data, and population-weighted census geography are shared with live scenarios. Training is never started by the default application stack.

```bash
python training/train_rl_agent.py --timesteps 50000 --seed 2025 --output models/ppo_seird
```

The trainer writes a Stable-Baselines3 checkpoint and a sibling metadata JSON file containing the model version and source-data fingerprint. A checkpoint is not loaded by the API automatically; validate observation order, action mapping, source fingerprint, format version, and evaluation results before deployment.
