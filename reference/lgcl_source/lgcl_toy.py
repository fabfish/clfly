"""LGCL: 线性-高斯持续学习最小可解模型 —— 实验复现代码
依赖: numpy, matplotlib
"""
import numpy as np
from numpy.linalg import inv, eigh
import matplotlib.pyplot as plt

def make_tasks(d, T, n, sigma2, spectrum_decay=0.85, rotation_mode="random", alpha=None, rng=None):
    """为每个任务生成输入协方差 Sigma_k = U_k diag(s) U_k^T 与信息精度 J_k = n*Sigma_k/sigma2"""
    rng = rng or np.random.default_rng()
    s = spectrum_decay ** np.arange(d)          # 衰减谱 → 低有效秩
    Sigmas, Js, Us = [], [], []
    U_prev = np.eye(d)
    for k in range(T):
        if rotation_mode == "random":
            A = rng.standard_normal((d, d)); U, _ = np.linalg.qr(A)
        elif rotation_mode == "axis":
            U = np.eye(d)
        elif rotation_mode == "angle":  # 在前两维平面内旋转 alpha
            U = np.eye(d)
            c, sn = np.cos(alpha), np.sin(alpha)
            U[:2, :2] = np.array([[c, -sn], [sn, c]])
        Sig = U @ np.diag(s) @ U.T
        Sigmas.append(Sig); Us.append(U)
        Js.append(n * Sig / sigma2)     # 期望 Fisher = 信息精度
    return Sigmas, Js, Us


def simulate(d, T, q, Sigmas, Js, sigma2, n, rng):
    """模拟真实漂移参数与每任务的充分统计量观测"""
    theta = rng.standard_normal(d)
    thetas, hats = [], []
    for k in range(T):
        thetas.append(theta.copy())
        # 观测: hat = theta + noise, cov = J_k^{-1}
        L = np.linalg.cholesky(inv(Js[k]))
        hats.append(theta + L @ rng.standard_normal(d))
        theta = theta + np.sqrt(q) * rng.standard_normal(d)   # 任务间漂移
    return thetas, hats


def kalman_update(th, P, J, h, project=None):
    """信息形式的 Kalman 更新; project: None | 'diag' | int(保留秩)"""
    Pinv = inv(P)
    Pn = inv(Pinv + J)
    thn = Pn @ (Pinv @ th + J @ h)
    if project == 'diag':
        Pn = np.diag(np.diag(Pn))
    elif isinstance(project, int) and project < Pn.shape[0]:
        w, U = eigh(Pn)
        keep = np.argsort(w)[::-1][:project]
        lam = w[keep]; c = np.mean(np.delete(w, keep))  # 弃方向摊平(注水)
        Pn = (U[:, keep] * lam) @ U[:, keep].T + c * (np.eye(len(Pn)) - U[:, keep] @ U[:, keep].T)
    return thn, Pn


def run_method(name, thetas, hats, Js, q, d, P0_scale=1.0, replay_budget=0, sketch_r=None):
    T = len(Js)
    th = np.zeros(d); P = P0_scale * np.eye(d)
    ests = []          # 每个时刻的估计
    store = []         # 回放仓库 (hat_j, J_j, time_j)
    for k in range(T):
        P = P + q * np.eye(d)                       # predict
        if name == 'naive':
            th = inv(Js[k]) @ (Js[k] @ hats[k]); P = inv(Js[k])
        elif name == 'replay':
            # 融合当前 + 仓库内旧观测(陈旧度膨胀: J_eff^{-1} = J_j^{-1} + (k-j)qI)
            Js_eff, hs = [Js[k]], [Js[k] @ hats[k]]
            for (hj, Jj, tj) in store[-replay_budget:] if replay_budget else []:
                Je = inv(inv(Jj) + (k - tj) * q * np.eye(d))
                Js_eff.append(Je); hs.append(Je @ hj)
            Pinv = inv(P) + sum(Js_eff) - Js[k]     # 当前测量走正常kalman,旧观测一次性融合
            # 简化: 先正常融合当前, 再融合旧观测
            th, P = kalman_update(th, P, Js[k], hats[k])
            for Je, hh in zip(Js_eff[1:], hs[1:]):
                th, P = kalman_update(th, P, Je, inv(Je) @ hh)
        elif name == 'kalman':
            th, P = kalman_update(th, P, Js[k], hats[k])
        elif name == 'ewc':
            th, P = kalman_update(th, P, Js[k], hats[k], project='diag')
        elif name == 'sketch':
            th, P = kalman_update(th, P, Js[k], hats[k], project=sketch_r)
        store.append((hats[k], Js[k], k))
        ests.append(th.copy())
    return ests


def evaluate(ests, thetas, Sigmas):
    """e_j(k) = (th_k - th_j)^T Sigma_j (th_k - th_j); 返回遗忘与最终平均误差"""
    T = len(ests); E = np.zeros((T, T))
    for k in range(T):
        for j in range(k+1):
            diff = ests[k] - thetas[j]
            E[k, j] = diff @ Sigmas[j] @ diff
    final_avg = np.mean([E[T-1, j] for j in range(T)])
    forgetting = np.mean([E[T-1, j] - E[j, j] for j in range(T-1)])
    return E, final_avg, forgetting


def mc_run(method_names, d=20, T=10, n=40, sigma2=1.0, q=0.05, runs=200, rotation_mode="random",
           alpha=None, replay_budget=3, sketch_r=4, seed0=0):
    out = {m: {'E': [], 'final': [], 'forget': []} for m in method_names}
    for r in range(runs):
        rng = np.random.default_rng(seed0 + r)
        Sigmas, Js, _ = make_tasks(d, T, n, sigma2, rotation_mode=rotation_mode, alpha=alpha, rng=rng)
        thetas, hats = simulate(d, T, q, Sigmas, Js, sigma2, n, rng)
        for m in method_names:
            ests = run_method(m, thetas, hats, Js, q, d,
                              replay_budget=replay_budget, sketch_r=sketch_r)
            E, fa, fg = evaluate(ests, thetas, Sigmas)
            out[m]['E'].append(E); out[m]['final'].append(fa); out[m]['forget'].append(fg)
    for m in method_names:
        out[m]['E'] = np.mean(out[m]['E'], axis=0)
        out[m]['final'] = (np.mean(out[m]['final']), np.std(out[m]['final'])/np.sqrt(runs))
        out[m]['forget'] = (np.mean(out[m]['forget']), np.std(out[m]['forget'])/np.sqrt(runs))
    return out


def make_tasks_rot(d, T, n, sigma2, s, alpha_step):
    """任务 k 的精度特征基相对坐标轴累积旋转 k*alpha_step"""
    Sigmas, Js = [], []
    for k in range(T):
        a = k * alpha_step
        U = np.eye(d); c, sn = np.cos(a), np.sin(a)
        U[:2,:2] = np.array([[c,-sn],[sn,c]])
        Sig = U @ np.diag(s) @ U.T
        Sigmas.append(Sig); Js.append(n * Sig / sigma2)
    return Sigmas, Js


def make_tasks_partial(d, T, n, sigma2, obs_dim, rng):
    Sigmas, Js = [], []
    for k in range(T):
        A = rng.standard_normal((d, d)); U, _ = np.linalg.qr(A)
        P_obs = U[:, :obs_dim] @ U[:, :obs_dim].T      # 观测子空间投影
        Sigmas.append(P_obs)                            # 评估权重: 该任务关心的方向
        Js.append((n/sigma2) * P_obs)
    return Sigmas, Js


def simulate_partial(d, T, Js, obs_dim, rng):
    theta = rng.standard_normal(d)
    thetas = [theta.copy() for _ in range(T)]
    hats = []
    for k in range(T):
        # 只在观测子空间内有噪声: hat = theta + U_obs * noise / sqrt(n/sigma2)
        w, U = eigh(Js[k])
        idx = np.argsort(w)[::-1][:obs_dim]
        Uo = U[:, idx]
        hats.append(theta + Uo @ (rng.standard_normal(obs_dim) / np.sqrt(n/sigma2)))
    return thetas, hats

