"""Diagnostic: per-step trace of coverage rate for classical vs RL policies."""
import argparse
import numpy as np

from utils.config_loader import load_config
from envs.maps import create_map
from envs.continuous_env import ContinuousSearchEnv
from algorithms import create_algorithm


def build(env_config, seed):
    cfg = load_config(env_config)
    map_obj = create_map(cfg["map"]["type"], cfg["map"])
    env = ContinuousSearchEnv(map_obj, cfg)
    obs, info = env.reset(seed=seed)
    return env, map_obj, cfg, obs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--algo", default="oracle_coverage")
    ap.add_argument("--checkpoint", default=None)
    ap.add_argument("--env-config", default="config/env/continuous_square.yaml")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-steps", type=int, default=300)
    ap.add_argument("--every", type=int, default=5)
    args = ap.parse_args()

    env, map_obj, cfg, obs = build(args.env_config, args.seed)
    if args.algo in ("dqn", "sac"):
        from algorithms.dqn import DQNAgent
        from algorithms.sac import SACAgent
        agent = (DQNAgent if args.algo == "dqn" else SACAgent)(
            env.observation_space.shape[0], env.action_space.n,
            load_config(f"config/algo/{args.algo}.yaml"))
        agent.load(args.checkpoint)
        policy = lambda o: agent.select_action(o, deterministic=True)
    else:
        algo_cfg = dict(cfg)
        algo_cfg.update({
            "num_actions": env.action_space.n,
            "resolution": cfg["map"]["resolution"],
            "map_length": cfg["map"]["length"],
            "action_angles": [-90, -45, 0, 45, 90],
            "map_obj": map_obj,
            "sonar": cfg["sonar"],
            "grid_shape": map_obj.grid.shape,
            "obs_patch_radius": cfg.get("obs_patch_radius", 5),
        })
        algo = create_algorithm(args.algo, algo_cfg)
        policy = lambda o: algo.select_action(o)

    cov = env.info_map.coverage
    prev = cov.copy()
    total = int(cov.sum())
    print(f"free={total} start={np.round(env.auv_state[:2] / cfg['map']['resolution'] - 0.5, 1)}")
    for t in range(args.max_steps):
        a = policy(obs)
        obs, r, term, trunc, info = env.step(a)
        cov = env.info_map.coverage
        new = int(cov.sum() - prev.sum())
        prev = cov.copy()
        if t % args.every == 0 or info.get("detected") or info.get("collision"):
            r0, c0 = env.auv_state[1] / cfg["map"]["resolution"] - 0.5, env.auv_state[0] / cfg["map"]["resolution"] - 0.5
            print(f"t={t:3d} a={a} pos=({r0:5.1f},{c0:5.1f}) new={new:2d} cov={cov.mean():.3f}"
                  f"{' COLL' if info.get('collision') else ''}{' FOUND' if info.get('detected') else ''}")
        if term or trunc:
            print(f"end t={t} term={term} cov={cov.mean():.3f}")
            break


if __name__ == "__main__":
    main()
