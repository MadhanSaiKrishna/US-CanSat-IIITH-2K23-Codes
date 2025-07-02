import numpy as np
import matplotlib.pyplot as plt

n = 1.4
R = 8314.47
V = 30
k = n*R/V

def time():
    return np.random.randint(0, 100)

def f(r):
    return 120 * (r/10)**2 * np.exp(-r/10)

r = np.linspace(8, 100, 93)
T = f(r)+np.random.random(len(r))
P = k*(T + 273) + np.random.random(len(r))*400

# plt.plot(r, T)
plt.plot(r, P)
plt.xlabel('r')
plt.ylabel('f(r)')
plt.title('f(r) vs r')
plt.show()
plt.close()

print(r)