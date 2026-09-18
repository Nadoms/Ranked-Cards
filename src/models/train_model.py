import json
from os import path
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import sys


PROJECT_DIR = Path(__file__).resolve().parent.parent


def train(data_oi, data, filename="models.json"):
    X_data = []
    Y_data = []
    for item in data:
        if item[1] >= 0.75:
            X_data.append(item[0])
            Y_data.append(item[1])
    order = np.argsort(X_data)
    X = np.array(X_data)[order]
    Y = np.array(Y_data)[order]

    W = np.array([0.2, -0.25, 0.75])
    step_sizes = np.array([0.01, 0.1, 0.1])
    loss_list = []
    iter = 30000

    max_y = max(Y)
    for i in range(iter):
        Y_pred = forward(X, W)
        elo_weights = 2 * (Y / max_y) ** 4
        loss = np.mean(elo_weights * np.abs(Y_pred - Y))
        loss_list.append(loss)

        W_grad = np.array([
            np.mean(elo_weights * (Y_pred - Y) * (1 / (X + W[1]))),
            np.mean(elo_weights * (Y_pred - Y) * (-W[0] / (X + W[1])**2)),
            np.mean(elo_weights * (Y_pred - Y))
        ])

        W = W - step_sizes * W_grad

        if i % 1000 == 0:
            print(f"{i},\t{loss},\t{W.tolist()}")

    plt.plot(X, Y, "b.", label="Y")
    plt.plot(X, Y_pred, "y", label="pred", linewidth=3)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.grid(True, color="y")
    plt.savefig(PROJECT_DIR / "models" / f"model_{data_oi}.png")
    plt.close()

    update_weights(data_oi, filename, W, y=True)


def forward(X, W):
    return W[0] / (X + W[1]) + W[2]


def regular_forward(x, W):
    for i in range(len(W)):
        sum += W[i] * (x ** (i - 1))


def criterion(Y_pred, Y):
    return np.mean(np.abs(Y_pred - Y))


def update_weights(data_oi, filename: str, W, y=False):
    weight_mapping = "abcdefghijklmnopqrstuvwxyz"  # ???

    file = (PROJECT_DIR / "models" / filename)
    if file.exists():
        with open(file, "r") as f:
            models = json.load(f)

        if data_oi in models:
            print("Do you wanna update your model?\nOld and new values are:")
            for key in models[data_oi]:
                print(f"{models[data_oi][key]}\t", end="")
            print()
            for w in W:
                print(f"{w.item()}\t", end="")
    else:
        models = {data_oi: {}}

    if y or input("\n(Y) or (Any key) :: ") == "Y" or not file.exists():
        models.update({
            data_oi: {
                weight_mapping[i]: W[i].item()
                for i in range(len(W))
            }
        })
        with open(file, "w") as f:
            json.dump(models, f, indent=4)
        print("Updated!")
    else:
        print("Okay...")


def main(data_oi):
    playerbase_file = PROJECT_DIR / "database" / "playerbase.json"
    with open(playerbase_file, "r") as f:
        playerbase_data = json.load(f)

    data_ois = playerbase_data["stats"][data_oi]
    elos = playerbase_data["stats"]["elo"]
    uuids = list(data_ois.keys()) if data_oi == "avg" else list(elos.keys())

    train(
        data_oi,
        [(data_ois[uuid] * 1e-6, elos[uuid] * 1e-3) for uuid in uuids]
    )


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        data_oi = sys.argv[1]
    else:
        print("Usage: python generate_model.py <data of interest>")
    main(data_oi)
