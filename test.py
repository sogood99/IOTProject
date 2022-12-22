import numpy as np
import matplotlib.pyplot as plt


def predict(x, p):
    return p[0] * x + p[1]


y = [90]*4 + [60]*5+[30]*5
x = [12820, 12821, 12822, 12824] + [12789, 12788, 12786,
                                    12787, 12787] + [12736, 12737, 12739, 12739, 12736]

p = np.polyfit(x, y, 1)
xf = np.linspace(12680, 13000, 1000)
print(p)
plt.scatter(x, y)
plt.plot(xf, predict(xf, p), '--', color='orange')
plt.savefig("fig.png")
plt.show()

print(predict(12887, p))
