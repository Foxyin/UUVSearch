"""
UUVSearch - 统一评测 harness

对任意算法（传统基线 / RL checkpoint）在指定环境配置上跑 N 个回合，
输出统一的指标表 + JSON（含逐回合原始数据，便于后续统计检验）。

指标：
  success            是否发现目标
  steps              回合步数（失败= max_steps）
  steps_success      仅成功回合的步数（条件步数，主指标）
  coverage_end       回合结束时自由格覆盖率
  coverage_detected  发现目标时的覆盖率（仅成功回合）
  collisions         碰撞次数
  path_len_m         航行距离（米）

回合 ep 使用 env.reset(seed=seed+ep)，与 evaluate.py / run_experiment.py 一致。

用法:
  python scripts/benchmark.py --algo bayes_myopic --episodes 200 --seed 0
  python scripts/benchmark.py --algo dqn --checkpoint experiments/checkpoints/dqn_v6/best.pt \
      --episodes 200 --env-config config/env/continuous_square.yaml --tag dqn_v6_square
"""
import sys
import os
import json
import time
import argparse
import datetime

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.config_loader import load_config
from envs.maps import create_map
from envs.continuous_env import ContinuousSearchEnv
from algorithms import create_algorithm


CLASSICAL = ["random", "lawnmower", "greedy_prob", "oracle_coverage", "bayes_myopic"]
RL = ["dqn", "sac"]


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def build_classical(name, cfg, map_obj):
    acfg = {
        "num_actions": 5,
        "resolution": cfg["map"]["resolution"],
        "map_length": cfg["map"]["length"],
        "action_angles": [-90, -45, 0, 45, 90],
        "sonar": cfg["sonar"],
        "grid_shape": map_obj.grid.shape,
        "obs_patch_radius": cfg.get("obs_patch_radius", 5),
    }
    if name in ("lawnmower", "oracle_coverage", "greedy_prob"):
        acfg["map_obj"] = map_obj
    return create_algorithm(name, acfg)


def build_rl(name, env, checkpoint):
    if name == "dqn":
        from algorithms.dqn.agent import DQNAgent
        algo_cfg = load_config("config/algo/dqn.yaml")
        agent = DQNAgent(env.observation_space.shape[0], env.action_space.n, algo_cfg)
    else:
        from algorithms.sac.agent import SACAgent
        algo_cfg = load_config("config/algo/sac.yaml")
        agent = SACAgent(env.observation_space.shape[0], env.action_space.n, algo_cfg)
    agent.load(checkpoint)
    return agent


def run(algo_name, algo, env, episodes, seed, max_steps, verbose=True):
    free_mask = env.map.get_mask()
    records = []
    t0 = time.time()
    for ep in range(episodes):
        np.random.seed(seed + ep)
        obs, _ = env.reset(seed=seed + ep)
        if hasattr(algo, "reset"):
            algo.reset()

        collisions = 0
        found = False
        for _ in range(max_steps):
            if hasattr(algo, "select_action"):
                if algo_name in RL:
                    action = algo.select_action(obs, deterministic=True)
                else:
                    action = algo.select_action(obs)
            else:
                action = algo.select_action(obs)
            obs, reward, terminated, truncated, info = env.step(action)
            if info.get("collision", False):
                collisions += 1
            if terminated or truncated:
                found = bool(terminated and info.get("detected", False))
                break

        cov = float(env.info_map.coverage[free_mask].mean())
        records.append({
            "episode": ep,
            "seed": seed + ep,
            "success": int(found),
            "steps": int(env.step_count),
            "coverage_end": cov,
            "coverage_detected": cov if found else None,
            "collisions": collisions,
        })
        if verbose and (ep + 1) % 50 == 0:
            print(f"  [{algo_name}] {ep + 1}/{episodes} episodes "
                  f"({time.time() - t0:.1f}s)", flush=True)

    succ = np.array([r["success"] for r in records])
    steps = np.array([r["steps"] for r in records])
    steps_s = np.array([r["steps"] for r in records if r["success"]])
    cov_end = np.array([r["coverage_end"] for r in records])
    cov_det = np.array([r["coverage_detected"] for r in records if r["success"]])
    coll = np.array([r["collisions"] for r in records])

    k = int(succ.sum())
    lo, hi = wilson_ci(k, len(records))
    return {
        "algo": algo_name,
        "episodes": len(records),
        "success_rate": k / len(records),
        "success_ci95": [lo, hi],
        "steps_mean": float(steps.mean()),
        "steps_std": float(steps.std()),
        "steps_success_mean": float(steps_s.mean()) if len(steps_s) else None,
        "steps_success_std": float(steps_s.std()) if len(steps_s) else None,
        "steps_success_median": float(np.median(steps_s)) if len(steps_s) else None,
        "coverage_end_mean": float(cov_end.mean()),
        "coverage_detected_mean": float(cov_det.mean()) if len(cov_det) else None,
        "collisions_mean": float(coll.mean()),
        "wall_time_s": round(time.time() - t0, 1),
        "records": records,
    }


def main():
    parser = argparse.ArgumentParser(description="UUVSearch 统一评测 harness")
    parser.add_argument("--algo", required=True, choices=CLASSICAL + RL)
    parser.add_argument("--checkpoint", default=None, help="RL checkpoint 路径")
    parser.add_argument("--env-config", default="config/env/continuous_square.yaml")
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0, help="基准种子，回合 ep 用 seed+ep")
    parser.add_argument("--tag", default=None, help="输出文件名（不含扩展名）")
    parser.add_argument("--out-dir", default="experiments/benchmark")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.env_config)
    map_obj = create_map(cfg["map"]["type"], cfg["map"])
    env = ContinuousSearchEnv(map_obj, cfg)
    max_steps = cfg["simulation"]["max_steps"]

    if args.algo in RL:
        if not args.checkpoint:
            parser.error("RL 算法需要 --checkpoint")
        algo = build_rl(args.algo, env, args.checkpoint)
        source = args.checkpoint
    else:
        algo = build_classical(args.algo, cfg, map_obj)
        source = None

    print(f"== {args.algo} | {args.env_config} | {args.episodes} eps | seed {args.seed} ==")
    summary = run(args.algo, algo, env, args.episodes, args.seed, max_steps,
                  verbose=not args.quiet)

    name = args.tag or f"{args.algo}_{os.path.splitext(os.path.basename(args.env_config))[0]}"
    os.makedirs(args.out_dir, exist_ok=True)
    payload = {
        "meta": {
            "algo": args.algo,
            "checkpoint": source,
            "env_config": args.env_config,
            "episodes": args.episodes,
            "seed": args.seed,
            "max_steps": max_steps,
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        },
        "summary": {k: v for k, v in summary.items() if k != "records"},
        "records": summary["records"],
    }
    path = os.path.join(args.out_dir, name + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    s = summary
    print(f"{'algo':<16}{'succ':>8}{'95%CI':>16}{'steps':>9}{'steps|succ':>12}"
          f"{'cov_end':>9}{'cov@det':>9}{'coll':>7}")
    ci = f"[{s['success_ci95'][0]:.3f},{s['success_ci95'][1]:.3f}]"
    ss = "—" if s["steps_success_mean"] is None else f"{s['steps_success_mean']:.1f}"
    cd = "—" if s["coverage_detected_mean"] is None else f"{s['coverage_detected_mean']:.3f}"
    print(f"{s['algo']:<16}{s['success_rate']:>8.3f}{ci:>16}{s['steps_mean']:>9.1f}"
          f"{ss:>12}{s['coverage_end_mean']:>9.3f}{cd:>9}{s['collisions_mean']:>7.2f}")
    print(f"→ {path}")


if __name__ == "__main__":
    main()
