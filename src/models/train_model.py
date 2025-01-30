import json
from os import path
from pathlib import Path
import torch
import numpy as np
import matplotlib.pyplot as plt
import sys


PROJECT_DIR = Path(__file__).resolve().parent.parent


def train(data_oi, X_data, Y_data):
    # Casting and plotting the data.
    order = np.argsort(X_data)
    X = torch.FloatTensor(X_data)[order]
    Y_raw = torch.FloatTensor(Y_data)[order]
    Y = Y_raw.apply_(lambda x: x * 1e-3)
    print(X, Y)

    W = [
        torch.tensor(0.0, requires_grad=True),
        torch.tensor(0.0, requires_grad=True),
        torch.tensor(0.0, requires_grad=True),
    ]

    step_sizes = [0.1, 0.1, 0.1]
    loss_list = []
    iter = 10000

    for i in range(iter):
        Y_pred = forward(X, W)
        loss = criterion(Y_pred, Y)
        loss_list.append(loss.item())
        loss.backward()

        for j in range(len(W)):
            W[j].data = W[j].data - step_sizes[j] * W[j].grad.data
            W[j].grad.data.zero_()

        if i % 1000 == 0:
            print(f"{i},\t{loss.item()},\t{[w.item() for w in W]}")

    plt.plot(X.numpy(), Y.numpy(), "b.", label="Y")
    plt.plot(X.numpy(), Y_pred.detach().numpy(), "y", label="pred", linewidth=3)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.grid("True", color="y")
    plt.savefig(PROJECT_DIR / "models" / f"model_{data_oi}.png")
    plt.show()
    plt.close()

    update_weights(data_oi, W, y=True)


# Defining the functions for forward pass for prediction
def forward(x, W):
    sum = 0
    sum = W[0] / (x + W[1]) + W[2]
    return sum


def regular_forward(x, W):
    for i in range(len(W)):
        sum += W[i] * (x ** (i - 1))


# Evaluating data points with MSE
def criterion(y_pred, y):
    return torch.mean((y_pred - y) ** 2)


def update_weights(data_oi, W, y=False):
    weight_mapping = "abcdefghijklmnopqrstuvwxyz"

    file = path.join("src", "models", "models.json")
    with open(file, "r") as f:
        models = json.load(f)

    print("Do you wanna update your model?\nOld and new values are:")
    for key in models[data_oi]:
        print(f"{models[data_oi][key]}\t", end="")
    print()
    for w in W:
        print(f"{w.item()}\t", end="")

    if y or input("\n(Y) or (Any key) :: ") == "Y":
        for i in range(len(W)):
            models[data_oi][weight_mapping[i]] = W[i].item()
        with open(file, "w") as f:
            models_json = json.dumps(models, indent=4)
            f.write(models_json)
        print("Updated!")
    else:
        print("Okay...")


def main(data_oi):
    data = [[], []]
    data_path = path.join(PROJECT_DIR / "models" / f"{data_oi}_vs_elo.txt")
    with open(data_path, "r") as f:
        while True:
            line = f.readline().strip().split(" ")
            if not line[0]:
                break

            data[0].append(int(line[0]))
            data[1].append(int(float(line[1])))

    train(data_oi, *data)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        data_oi = sys.argv[1]
    else:
        print("Usage: python generate_model.py <data of interest>")
    main(data_oi)
