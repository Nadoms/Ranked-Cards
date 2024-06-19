import torch
import numpy as np
import matplotlib.pyplot as plt
import sys


def main(path):
    # Getting the data into two arrays
    data = [[], []]
    with open(path, "r") as f:
        while True:
            line = f.readline().strip().split(" ")
            if not line[0]:
                break

            data[0].append(int(line[0]))
            data[1].append(int(line[1]))

    # Casting and plotting the data.
    order = np.argsort(data[0])
    X_raw = torch.FloatTensor(data[0])[order]
    Y_raw = torch.FloatTensor(data[1])[order]
    X = X_raw.apply_(lambda x : x * 1e-5)
    Y = Y_raw.apply_(lambda x : x * 1e-3)

    W = [torch.tensor(0.0, requires_grad=True),
         torch.tensor(0.0, requires_grad=True),
         torch.tensor(0.0, requires_grad=True)]

    step_sizes = [0.01, 0.01, 0.001]
    loss_list = []
    iter = 200
    
    for i in range(iter):
        Y_pred = forward(X, W)
        loss = criterion(Y_pred, Y)
        loss_list.append(loss.item())
        loss.backward()
        
        for j in range(len(W)):
            W[j].data = W[j].data - step_sizes[j] * W[j].grad.data
            W[j].grad.data.zero_()
            
        print(f"{i},\t{loss.item()},\t{[w.item() for w in W]}")

    # Plotting the loss after each iteration
    # plt.plot(loss_list, 'r')
    # plt.tight_layout()
    # plt.grid('True', color='y')
    # plt.xlabel("Epochs/Iterations")
    # plt.ylabel("Loss")
    # plt.show()
    
    plt.plot(X.numpy(), Y.numpy(), 'b.', label='Y')
    plt.plot(X.numpy(), Y_pred.detach().numpy(), 'y', label='pred', linewidth=3)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid('True', color='y')
    plt.show()


# Defining the function for forward pass for prediction
def forward(x, W):
    sum = 0
    for i in range(len(W)):
        sum += W[i] * (x ** (i-1))
    return sum


# Evaluating data points with MSE
def criterion(y_pred, y):
    return torch.mean((y_pred - y) ** 2)


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) >= 2:
        path = sys.argv[1]
    else:
        print("Usage: python generate_model.py <filepath>")
    main(path)